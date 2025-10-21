#!/usr/bin/env python3
"""
Advanced Selenium + selenium-wire site crawler & comprehensive data extractor.

Features:
- Deep dynamic content extraction with JavaScript execution
- Form structure analysis (fields, validation, submission flows)
- Interactive element mapping (modals, dropdowns, tabs)
- Component analysis (React/Vue/Svelte props and state)
- Complete API payload capture with request/response context
- Visual element extraction (CSS, animations, responsive breakpoints)
- User journey simulation (login flows, multi-step processes)
- Local storage and session data capture
- Real-time content updates (WebSocket, SSE)

Usage:
  python crawl_site_advanced.py --url https://habitsofmindai.netlify.app/ --out ./dump_advanced --deep
"""

import argparse
import json
import time
import re
import hashlib
import contextlib
import base64
import os
from pathlib import Path
from urllib.parse import urlparse, urljoin, urldefrag
from collections import deque, defaultdict
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Set

from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# ---------- Data Structures ----------

@dataclass
class FormField:
    name: str
    type: str
    required: bool
    placeholder: str
    value: str
    validation: Dict[str, Any]
    options: List[str]  # For select/radio
    attributes: Dict[str, str]

@dataclass
class FormStructure:
    action: str
    method: str
    fields: List[FormField]
    submit_selectors: List[str]
    validation_rules: Dict[str, Any]
    csrf_token: Optional[str]

@dataclass
class InteractiveElement:
    selector: str
    type: str  # button, modal, dropdown, tab, etc.
    trigger_event: str
    content_before: str
    content_after: str
    api_calls_triggered: List[str]
    css_changes: List[str]

@dataclass
class ComponentInfo:
    framework: str  # react, vue, svelte, angular
    component_name: str
    props: Dict[str, Any]
    state: Dict[str, Any]
    hooks_used: List[str]
    element_selector: str

@dataclass
class APICall:
    detected_at: str
    method: str
    url: str
    status: Optional[int]
    request_headers: Dict[str, str]
    response_headers: Dict[str, str]
    request_body: Optional[str]
    response_body: Optional[str]
    context: str  # page_load, user_interaction, component_mount, etc.
    triggered_by: Optional[str]  # selector or event that triggered this call
    timing: Dict[str, float]  # start_time, end_time, duration
    count: int
    last_seen: str

@dataclass
class PageAnalysis:
    url: str
    title: str
    captured_at: str
    html_content: str
    visible_text: str
    meta_tags: Dict[str, str]
    forms: List[FormStructure]
    interactive_elements: List[InteractiveElement]
    components: List[ComponentInfo]
    css_files: List[str]
    js_files: List[str]
    images: List[str]
    local_storage: Dict[str, str]
    session_storage: Dict[str, str]
    cookies: List[Dict[str, Any]]
    console_logs: List[Dict[str, str]]
    network_timing: Dict[str, float]
    responsive_breakpoints: List[int]
    accessibility_info: Dict[str, Any]
    seo_info: Dict[str, Any]

# ---------- Advanced Utils ----------

def now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def same_origin(a: str, b: str) -> bool:
    pa, pb = urlparse(a), urlparse(b)
    return (pa.scheme, pa.netloc) == (pb.scheme, pb.netloc)

def is_probably_asset(url: str) -> bool:
    url = url.split("?", 1)[0].lower()
    return url.endswith((
        ".png",".jpg",".jpeg",".gif",".svg",".webp",".ico",".avif",
        ".css",".js",".map",".woff",".woff2",".ttf",".otf",".eot",
        ".mp4",".webm",".mp3",".m4a",".pdf",".zip",".tar",".gz"
    ))

def slugify_url(url: str) -> str:
    u = urlparse(url)
    path = u.path or "/"
    q = f"?{u.query}" if u.query else ""
    base = f"{u.scheme}__{u.netloc}{path}{q}"
    s = re.sub(r"[^a-zA-Z0-9_\-./?=]", "_", base).strip("/")
    s = s.replace("/", "__").replace("?", "__q__").replace("=", "__eq__")
    if len(s) > 180:
        h = hashlib.sha1(base.encode()).hexdigest()[:10]
        s = s[:160] + "__" + h
    return s or "root"

def safe_text(s: Any, max_len: int = 10000) -> str:
    if s is None:
        return ""
    if isinstance(s, bytes):
        try:
            s = s.decode("utf-8", "replace")
        except:
            s = "<binary>"
    s = str(s)
    return s if len(s) <= max_len else s[:max_len] + f"... [truncated {len(s)-max_len} chars]"

def extract_component_info(driver, element) -> Optional[ComponentInfo]:
    """Extract React/Vue/Svelte component information from DOM element"""
    try:
        # Check for React
        react_props = driver.execute_script("""
            var el = arguments[0];
            if (el._reactInternalFiber) {
                return {
                    framework: 'react',
                    props: el._reactInternalFiber.memoizedProps || {},
                    state: el._reactInternalFiber.memoizedState || {},
                    type: el._reactInternalFiber.type?.name || 'Unknown'
                };
            }
            if (el.__reactInternalInstance) {
                return {
                    framework: 'react',
                    props: el.__reactInternalInstance._currentElement?.props || {},
                    state: el.__reactInternalInstance._instance?.state || {},
                    type: el.__reactInternalInstance._currentElement?.type?.name || 'Unknown'
                };
            }
            return null;
        """, element)
        
        if react_props:
            return ComponentInfo(
                framework="react",
                component_name=react_props.get("type", "Unknown"),
                props=react_props.get("props", {}),
                state=react_props.get("state", {}),
                hooks_used=[],
                element_selector=get_element_selector(driver, element)
            )

        # Check for Vue
        vue_info = driver.execute_script("""
            var el = arguments[0];
            if (el.__vue__) {
                return {
                    framework: 'vue',
                    props: el.__vue__.$props || {},
                    data: el.__vue__.$data || {},
                    computed: Object.keys(el.__vue__.$options.computed || {}),
                    methods: Object.keys(el.__vue__.$options.methods || {}),
                    component: el.__vue__.$options.name || 'Unknown'
                };
            }
            return null;
        """, element)
        
        if vue_info:
            return ComponentInfo(
                framework="vue",
                component_name=vue_info.get("component", "Unknown"),
                props=vue_info.get("props", {}),
                state=vue_info.get("data", {}),
                hooks_used=vue_info.get("computed", []) + vue_info.get("methods", []),
                element_selector=get_element_selector(driver, element)
            )

        # Check for Svelte (harder to detect, look for svelte-specific attributes)
        svelte_info = driver.execute_script("""
            var el = arguments[0];
            var svelteData = {};
            
            // Look for Svelte-specific data attributes
            Array.from(el.attributes).forEach(attr => {
                if (attr.name.startsWith('svelte-') || attr.name.startsWith('data-svelte')) {
                    svelteData[attr.name] = attr.value;
                }
            });
            
            if (Object.keys(svelteData).length > 0 || el.classList.contains('svelte-')) {
                return {
                    framework: 'svelte',
                    attributes: svelteData,
                    classes: Array.from(el.classList).filter(c => c.includes('svelte'))
                };
            }
            
            return null;
        """, element)
        
        if svelte_info:
            return ComponentInfo(
                framework="svelte",
                component_name="SvelteComponent",
                props=svelte_info.get("attributes", {}),
                state={},
                hooks_used=[],
                element_selector=get_element_selector(driver, element)
            )
            
    except Exception as e:
        pass
    
    return None

def get_element_selector(driver, element) -> str:
    """Generate a unique CSS selector for an element"""
    try:
        return driver.execute_script("""
            function getSelector(el) {
                if (el.id) return '#' + el.id;
                
                var path = [];
                while (el.nodeType === 1) {
                    var selector = el.nodeName.toLowerCase();
                    if (el.className) {
                        selector += '.' + el.className.split(' ').join('.');
                    }
                    
                    var parent = el.parentNode;
                    if (parent) {
                        var siblings = Array.from(parent.children).filter(child => 
                            child.nodeName === el.nodeName && 
                            child.className === el.className
                        );
                        if (siblings.length > 1) {
                            var index = siblings.indexOf(el) + 1;
                            selector += ':nth-of-type(' + index + ')';
                        }
                    }
                    
                    path.unshift(selector);
                    el = parent;
                    
                    if (!el || el.nodeType !== 1) break;
                }
                
                return path.join(' > ');
            }
            return getSelector(arguments[0]);
        """, element)
    except:
        return "unknown"

# ---------- Advanced API Store ----------

class AdvancedApiStore:
    def __init__(self):
        self._by_key = {}
        self._context_map = defaultdict(list)
        self._timing_data = {}

    def _key(self, method: str, url: str) -> str:
        return f"{method.upper()} {urldefrag(url)[0]}"

    def add(self, call: APICall):
        k = self._key(call.method, call.url)
        if k not in self._by_key:
            self._by_key[k] = call
        else:
            existing = self._by_key[k]
            existing.count += 1
            existing.last_seen = call.last_seen
            
            # Preserve the most informative request/response bodies
            if not existing.request_body and call.request_body:
                existing.request_body = call.request_body
            if not existing.response_body and call.response_body:
                existing.response_body = call.response_body
            if not existing.status and call.status:
                existing.status = call.status

        # Track context
        self._context_map[call.context].append(k)

    def get_by_context(self, context: str) -> List[APICall]:
        return [self._by_key[k] for k in self._context_map[context] if k in self._by_key]

    def to_list(self) -> List[APICall]:
        return sorted([asdict(call) for call in self._by_key.values()], 
                     key=lambda x: (x["method"], x["url"]))

# ---------- Advanced Crawler ----------

class AdvancedCrawler:
    def __init__(self, base_url: str, out_dir: str, max_pages: int, deep_analysis: bool, 
                 nav_timeout: int, interaction_delay: float):
        self.base_url = base_url.rstrip("/")
        self.parsed_base = urlparse(self.base_url)
        self.out = Path(out_dir)
        self.max_pages = max_pages
        self.deep_analysis = deep_analysis
        self.nav_timeout = nav_timeout
        self.interaction_delay = interaction_delay

        ensure_dir(self.out / "pages")
        ensure_dir(self.out / "components")
        ensure_dir(self.out / "forms")
        ensure_dir(self.out / "interactions")
        
        self.site_map = set()
        self.visited = set()
        self.api_store = AdvancedApiStore()
        self.page_analyses = {}
        self.global_components = []
        self.user_flows = []

        self.sw_opts = {
            'request_storage': 'memory',
            'max_request_body_size': 5 * 1024 * 1024,  # 5MB
            'max_response_body_size': 5 * 1024 * 1024,  # 5MB
            'verify_ssl': True,
        }
        self.driver = None
        self.wait = None

    def _init_driver(self):
        opts = Options()
        if not self.deep_analysis:  # Only headless if not doing deep analysis
            opts.add_argument("--headless=new")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--window-size=1400,1000")
        opts.add_argument("--disable-web-security")
        opts.add_argument("--disable-features=VizDisplayCompositor")
        
        # Enable logging
        opts.add_argument("--enable-logging")
        opts.add_argument("--log-level=0")
        opts.add_experimental_option("useAutomationExtension", False)
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])

        from selenium.webdriver.chrome.service import Service
        driver_path = ChromeDriverManager().install()
        service = Service(driver_path)
        self.driver = webdriver.Chrome(
            service=service,
            options=opts,
            seleniumwire_options=self.sw_opts
        )
        self.driver.set_page_load_timeout(self.nav_timeout)
        self.wait = WebDriverWait(self.driver, 10)

    def _quit_driver(self):
        with contextlib.suppress(Exception):
            if self.driver:
                self.driver.quit()

    def crawl(self):
        """Main crawling orchestration"""
        self._init_driver()
        try:
            print(f"🚀 Starting advanced crawl of {self.base_url}")
            
            # First pass: Basic page discovery
            self._discover_pages()
            
            if self.deep_analysis:
                print("🔍 Starting deep analysis...")
                # Second pass: Deep analysis of each page
                for url in list(self.visited):
                    self._deep_analyze_page(url)
                
                # Third pass: User flow simulation
                self._simulate_user_flows()

        finally:
            self._quit_driver()
            self._write_comprehensive_output()

    def _discover_pages(self):
        """Phase 1: Discover all pages via BFS"""
        q = deque([self.base_url])
        
        while q and len(self.visited) < self.max_pages:
            url = q.popleft()
            if url in self.visited:
                continue
                
            print(f"📄 Discovering: {url}")
            self.visited.add(url)
            
            try:
                self._visit_page_basic(url)
                links = self._extract_all_links()
                
                for link in links:
                    if (link not in self.visited and 
                        len(self.visited) + len(q) < self.max_pages):
                        q.append(link)
                        self.site_map.add(link)
                        
            except Exception as e:
                print(f"❌ Error discovering {url}: {e}")

    def _visit_page_basic(self, url: str):
        """Basic page visit with network capture"""
        # Clear previous requests
        with contextlib.suppress(Exception):
            del self.driver.requests

        try:
            self.driver.get(url)
            
            # Wait for basic page load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Wait a bit more for dynamic content
            time.sleep(2)
            
        except Exception as e:
            print(f"⚠️  Load error {url}: {e}")
            
        # Capture basic page data
        self._capture_basic_page_data(url)
        self._capture_network_requests(url, "page_load")

    def _deep_analyze_page(self, url: str):
        """Phase 2: Deep analysis of a single page"""
        print(f"🔬 Deep analyzing: {url}")
        
        try:
            self.driver.get(url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)  # Let everything load
            
            analysis = PageAnalysis(
                url=url,
                title=self.driver.title,
                captured_at=now_iso(),
                html_content=self.driver.page_source,
                visible_text=self._extract_visible_text(),
                meta_tags=self._extract_meta_tags(),
                forms=self._analyze_forms(),
                interactive_elements=self._analyze_interactive_elements(),
                components=self._analyze_components(),
                css_files=self._extract_css_files(),
                js_files=self._extract_js_files(),
                images=self._extract_images(),
                local_storage=self._capture_local_storage(),
                session_storage=self._capture_session_storage(),
                cookies=self._capture_cookies(),
                console_logs=self._capture_console_logs(),
                network_timing=self._capture_network_timing(),
                responsive_breakpoints=self._test_responsive_breakpoints(),
                accessibility_info=self._analyze_accessibility(),
                seo_info=self._analyze_seo()
            )
            
            self.page_analyses[url] = analysis
            self._save_page_analysis(url, analysis)
            
        except Exception as e:
            print(f"❌ Deep analysis error for {url}: {e}")

    def _extract_all_links(self) -> Set[str]:
        """Extract all types of navigation links"""
        links = set()
        
        try:
            # Standard links
            for a in self.driver.find_elements(By.CSS_SELECTOR, "a[href]"):
                href = a.get_attribute("href")
                if href and not href.startswith(("javascript:", "#", "mailto:", "tel:")):
                    abs_url = urljoin(self.base_url, href)
                    abs_url, _ = urldefrag(abs_url)
                    if same_origin(self.base_url, abs_url) and not is_probably_asset(abs_url):
                        links.add(abs_url)
            
            # Navigation from JavaScript (SPA routes)
            spa_routes = self.driver.execute_script("""
                var routes = [];
                
                // Try to find React Router routes
                if (window.__REACT_ROUTER__) {
                    try {
                        routes = routes.concat(window.__REACT_ROUTER__.routes || []);
                    } catch(e) {}
                }
                
                // Try to find Vue Router routes  
                if (window.Vue && window.Vue.$router) {
                    try {
                        routes = routes.concat(window.Vue.$router.options.routes || []);
                    } catch(e) {}
                }
                
                // Look for route definitions in script tags
                var scripts = Array.from(document.querySelectorAll('script'));
                scripts.forEach(function(script) {
                    var text = script.textContent || '';
                    var routeMatches = text.match(/['"`]\/[^'"`\\s]+['"`]/g);
                    if (routeMatches) {
                        routes = routes.concat(routeMatches.map(r => r.slice(1, -1)));
                    }
                });
                
                return routes.filter(r => typeof r === 'string' && r.startsWith('/'));
            """)
            
            for route in spa_routes:
                if route.startswith('/'):
                    abs_url = urljoin(self.base_url, route)
                    if not is_probably_asset(abs_url):
                        links.add(abs_url)
                        
        except Exception as e:
            print(f"⚠️  Link extraction error: {e}")
            
        return links

    def _analyze_forms(self) -> List[FormStructure]:
        """Comprehensive form analysis"""
        forms = []
        
        try:
            form_elements = self.driver.find_elements(By.TAG_NAME, "form")
            
            for form_el in form_elements:
                fields = []
                
                # Analyze all input types
                inputs = form_el.find_elements(By.CSS_SELECTOR, 
                    "input, select, textarea, [contenteditable]")
                
                for inp in inputs:
                    field_type = inp.get_attribute("type") or inp.tag_name
                    name = inp.get_attribute("name") or inp.get_attribute("id") or ""
                    required = inp.get_attribute("required") is not None
                    placeholder = inp.get_attribute("placeholder") or ""
                    value = inp.get_attribute("value") or ""
                    
                    # Get validation attributes
                    validation = {}
                    for attr in ["pattern", "min", "max", "minlength", "maxlength", "step"]:
                        val = inp.get_attribute(attr)
                        if val:
                            validation[attr] = val
                    
                    # Get options for select/radio
                    options = []
                    if field_type == "select":
                        select = Select(inp)
                        options = [opt.text for opt in select.options]
                    elif field_type == "radio":
                        name_attr = inp.get_attribute("name")
                        if name_attr:
                            radios = form_el.find_elements(By.CSS_SELECTOR, 
                                f"input[type=radio][name='{name_attr}']")
                            options = [r.get_attribute("value") for r in radios]
                    
                    # Get all attributes
                    attributes = {}
                    try:
                        attributes = self.driver.execute_script("""
                            var attrs = {};
                            var el = arguments[0];
                            for (var i = 0; i < el.attributes.length; i++) {
                                var attr = el.attributes[i];
                                attrs[attr.name] = attr.value;
                            }
                            return attrs;
                        """, inp)
                    except:
                        pass
                    
                    fields.append(FormField(
                        name=name,
                        type=field_type,
                        required=required,
                        placeholder=placeholder,
                        value=value,
                        validation=validation,
                        options=options,
                        attributes=attributes
                    ))
                
                # Find submit buttons/elements
                submit_selectors = []
                submits = form_el.find_elements(By.CSS_SELECTOR, 
                    "input[type=submit], button[type=submit], button:not([type]), [role=button]")
                for submit in submits:
                    selector = get_element_selector(self.driver, submit)
                    submit_selectors.append(selector)
                
                # Look for CSRF tokens
                csrf_token = None
                csrf_inputs = form_el.find_elements(By.CSS_SELECTOR, 
                    "input[name*='csrf'], input[name*='token'], input[type=hidden]")
                for csrf in csrf_inputs:
                    name = csrf.get_attribute("name") or ""
                    if any(term in name.lower() for term in ["csrf", "token", "_token"]):
                        csrf_token = csrf.get_attribute("value")
                        break
                
                forms.append(FormStructure(
                    action=form_el.get_attribute("action") or "",
                    method=form_el.get_attribute("method") or "GET",
                    fields=fields,
                    submit_selectors=submit_selectors,
                    validation_rules={},  # Could be extended
                    csrf_token=csrf_token
                ))
                
        except Exception as e:
            print(f"⚠️  Form analysis error: {e}")
        
        return forms

    def _analyze_interactive_elements(self) -> List[InteractiveElement]:
        """Find and analyze interactive elements"""
        interactive_elements = []
        
        selectors_to_test = [
            ("button", "click", "button"),
            ("[data-testid*='modal']", "click", "modal"),
            ("[class*='modal'], [class*='popup'], [class*='dialog']", "click", "modal"),
            ("[class*='dropdown'], [class*='menu']", "click", "dropdown"), 
            ("[role='tab'], [class*='tab']", "click", "tab"),
            ("[class*='accordion'], [class*='collaps']", "click", "accordion"),
            ("input, select, textarea", "change", "input"),
            ("[contenteditable]", "input", "editor")
        ]
        
        for selector, event, element_type in selectors_to_test:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements[:5]:  # Limit to avoid too many interactions
                    if not element.is_displayed():
                        continue
                        
                    element_selector = get_element_selector(self.driver, element)
                    
                    # Capture content before interaction
                    content_before = safe_text(element.text)
                    
                    # Clear requests to track what this interaction triggers
                    with contextlib.suppress(Exception):
                        del self.driver.requests
                    
                    # Perform interaction
                    api_calls_triggered = []
                    css_changes = []
                    
                    try:
                        if event == "click":
                            self.driver.execute_script("arguments[0].click();", element)
                        elif event == "change" and element.tag_name == "select":
                            select = Select(element)
                            if len(select.options) > 1:
                                select.select_by_index(1)
                        elif event == "input":
                            element.clear()
                            element.send_keys("test input")
                        
                        time.sleep(self.interaction_delay)
                        
                        # Capture API calls triggered by interaction
                        for req in getattr(self.driver, "requests", []):
                            if not is_probably_asset(req.url):
                                api_calls_triggered.append(f"{req.method} {req.url}")
                        
                    except Exception as interaction_error:
                        print(f"⚠️  Interaction error on {element_selector}: {interaction_error}")
                    
                    # Capture content after interaction
                    content_after = safe_text(element.text)
                    
                    if (content_before != content_after or 
                        api_calls_triggered or 
                        element_type in ["modal", "dropdown"]):
                        
                        interactive_elements.append(InteractiveElement(
                            selector=element_selector,
                            type=element_type,
                            trigger_event=event,
                            content_before=content_before,
                            content_after=content_after,
                            api_calls_triggered=api_calls_triggered,
                            css_changes=css_changes
                        ))
                        
            except Exception as e:
                print(f"⚠️  Interactive element analysis error for {selector}: {e}")
        
        return interactive_elements

    def _analyze_components(self) -> List[ComponentInfo]:
        """Analyze frontend framework components"""
        components = []
        
        try:
            # Find potential component root elements
            component_selectors = [
                "[data-reactroot]", "[data-react-]", "[class*='react-']",
                "[data-vue-]", "[class*='vue-']", "[id*='vue']",
                "[class*='svelte-']", "[data-svelte-]",
                "[ng-app]", "[data-ng-]", "[class*='ng-']"
            ]
            
            for selector in component_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    component_info = extract_component_info(self.driver, element)
                    if component_info:
                        components.append(component_info)
                        
        except Exception as e:
            print(f"⚠️  Component analysis error: {e}")
        
        return components

    def _capture_network_requests(self, current_url: str, context: str, triggered_by: str = None):
        """Capture and analyze network requests"""
        for req in getattr(self.driver, "requests", []):
            if not req.url.startswith(("http://", "https://")):
                continue
            if is_probably_asset(req.url):
                continue
                
            method = (req.method or "GET").upper()
            request_headers = dict(req.headers) if req.headers else {}
            
            # Response analysis
            status = None
            response_headers = {}
            response_body = None
            timing = {}
            
            try:
                if req.response:
                    status = req.response.status_code
                    response_headers = dict(req.response.headers)
                    
                    # Only capture text-based responses
                    content_type = response_headers.get("content-type", "")
                    if any(t in content_type.lower() for t in 
                          ["json", "text", "xml", "html", "javascript"]):
                        response_body = safe_text(req.response.body)
                
                # Timing information
                if hasattr(req, 'date'):
                    timing['timestamp'] = req.date.timestamp()
                    
            except Exception as e:
                print(f"⚠️  Response analysis error: {e}")
            
            api_call = APICall(
                detected_at=now_iso(),
                method=method,
                url=urldefrag(req.url)[0],
                status=status,
                request_headers=request_headers,
                response_headers=response_headers,
                request_body=safe_text(getattr(req, "body", None), 5000),
                response_body=response_body,
                context=context,
                triggered_by=triggered_by,
                timing=timing,
                count=1,
                last_seen=now_iso()
            )
            
            self.api_store.add(api_call)

    def _simulate_user_flows(self):
        """Simulate common user journeys"""
        print("🎭 Simulating user flows...")
        
        # Common flows to test
        flows = [
            self._simulate_navigation_flow,
            self._simulate_form_submission_flow,
            self._simulate_search_flow,
            self._simulate_authentication_flow
        ]
        
        for flow in flows:
            try:
                flow_data = flow()
                if flow_data:
                    self.user_flows.append(flow_data)
            except Exception as e:
                print(f"⚠️  User flow simulation error: {e}")

    def _simulate_navigation_flow(self) -> Dict[str, Any]:
        """Simulate typical navigation patterns"""
        flow_data = {
            "flow_type": "navigation",
            "steps": [],
            "api_calls": [],
            "timestamp": now_iso()
        }
        
        # Visit main page and key sections
        key_pages = [self.base_url, f"{self.base_url}/about", f"{self.base_url}/contact"]
        
        for page in key_pages:
            if page in self.visited:
                try:
                    with contextlib.suppress(Exception):
                        del self.driver.requests
                    
                    self.driver.get(page)
                    time.sleep(2)
                    
                    step_data = {
                        "action": "navigate",
                        "url": page,
                        "timestamp": now_iso(),
                        "page_title": self.driver.title
                    }
                    
                    flow_data["steps"].append(step_data)
                    
                    # Capture API calls from navigation
                    for req in getattr(self.driver, "requests", []):
                        if not is_probably_asset(req.url):
                            flow_data["api_calls"].append({
                                "method": req.method,
                                "url": req.url,
                                "triggered_by": f"navigation to {page}"
                            })
                            
                except Exception as e:
                    print(f"⚠️  Navigation flow error for {page}: {e}")
        
        return flow_data

    def _simulate_form_submission_flow(self) -> Dict[str, Any]:
        """Test form submissions"""
        flow_data = {
            "flow_type": "form_submission", 
            "steps": [],
            "api_calls": [],
            "timestamp": now_iso()
        }
        
        # Look for contact forms, newsletter signups, etc.
        for url, analysis in self.page_analyses.items():
            if analysis.forms:
                try:
                    self.driver.get(url)
                    time.sleep(2)
                    
                    for i, form in enumerate(analysis.forms):
                        try:
                            # Find the form element
                            form_elements = self.driver.find_elements(By.TAG_NAME, "form")
                            if i < len(form_elements):
                                form_el = form_elements[i]
                                
                                # Fill out the form with test data
                                self._fill_form_with_test_data(form_el, form.fields)
                                
                                flow_data["steps"].append({
                                    "action": "fill_form",
                                    "url": url,
                                    "form_action": form.action,
                                    "fields_filled": len(form.fields)
                                })
                                
                                # Note: Not actually submitting to avoid spam
                                
                        except Exception as e:
                            print(f"⚠️  Form testing error: {e}")
                            
                except Exception as e:
                    print(f"⚠️  Form flow error for {url}: {e}")
        
        return flow_data

    def _fill_form_with_test_data(self, form_element, fields: List[FormField]):
        """Fill form with appropriate test data"""
        test_data = {
            "email": "test@example.com",
            "name": "Test User",
            "subject": "Test Subject",
            "message": "This is a test message",
            "phone": "555-0123",
            "company": "Test Company"
        }
        
        for field in fields:
            try:
                # Find the input element
                selectors = [
                    f"[name='{field.name}']",
                    f"[id='{field.name}']",
                    f"[placeholder*='{field.name}']"
                ]
                
                element = None
                for selector in selectors:
                    try:
                        element = form_element.find_element(By.CSS_SELECTOR, selector)
                        break
                    except NoSuchElementException:
                        continue
                
                if element and element.is_displayed():
                    # Fill based on field type and name
                    if field.type == "email" or "email" in field.name.lower():
                        element.clear()
                        element.send_keys(test_data["email"])
                    elif field.type == "text" or field.type == "input":
                        key = next((k for k in test_data.keys() 
                                   if k in field.name.lower()), "name")
                        element.clear()
                        element.send_keys(test_data.get(key, "Test Input"))
                    elif field.type == "textarea":
                        element.clear()
                        element.send_keys(test_data["message"])
                    elif field.type == "select" and field.options:
                        select = Select(element)
                        if len(select.options) > 1:
                            select.select_by_index(1)
                            
            except Exception as e:
                print(f"⚠️  Field fill error for {field.name}: {e}")

    def _simulate_search_flow(self) -> Dict[str, Any]:
        """Test search functionality"""
        # Implementation would test search boxes, filters, etc.
        return {"flow_type": "search", "steps": [], "timestamp": now_iso()}

    def _simulate_authentication_flow(self) -> Dict[str, Any]:
        """Test login/registration flows"""
        # Implementation would test login forms, social auth, etc.
        return {"flow_type": "authentication", "steps": [], "timestamp": now_iso()}

    # Helper methods for data extraction

    def _capture_basic_page_data(self, url: str):
        """Capture basic page information"""
        pass  # Implemented in _deep_analyze_page

    def _extract_visible_text(self) -> str:
        """Extract all visible text from page"""
        try:
            return self.driver.execute_script("""
                function getVisibleText(element) {
                    var text = '';
                    
                    if (element.nodeType === 3) { // Text node
                        return element.textContent;
                    }
                    
                    if (window.getComputedStyle(element).display === 'none' ||
                        window.getComputedStyle(element).visibility === 'hidden') {
                        return '';
                    }
                    
                    for (var i = 0; i < element.childNodes.length; i++) {
                        text += getVisibleText(element.childNodes[i]);
                    }
                    
                    return text;
                }
                
                return getVisibleText(document.body);
            """)
        except:
            return ""

    def _extract_meta_tags(self) -> Dict[str, str]:
        """Extract all meta tags"""
        meta_tags = {}
        try:
            metas = self.driver.find_elements(By.TAG_NAME, "meta")
            for meta in metas:
                name = (meta.get_attribute("name") or 
                       meta.get_attribute("property") or 
                       meta.get_attribute("http-equiv"))
                content = meta.get_attribute("content")
                if name and content:
                    meta_tags[name] = content
        except:
            pass
        return meta_tags

    def _extract_css_files(self) -> List[str]:
        """Extract all CSS file references"""
        css_files = []
        try:
            links = self.driver.find_elements(By.CSS_SELECTOR, "link[rel='stylesheet']")
            for link in links:
                href = link.get_attribute("href")
                if href:
                    css_files.append(href)
        except:
            pass
        return css_files

    def _extract_js_files(self) -> List[str]:
        """Extract all JavaScript file references"""
        js_files = []
        try:
            scripts = self.driver.find_elements(By.TAG_NAME, "script")
            for script in scripts:
                src = script.get_attribute("src")
                if src:
                    js_files.append(src)
        except:
            pass
        return js_files

    def _extract_images(self) -> List[str]:
        """Extract all image sources"""
        images = []
        try:
            imgs = self.driver.find_elements(By.TAG_NAME, "img")
            for img in imgs:
                src = img.get_attribute("src")
                if src:
                    images.append(src)
        except:
            pass
        return images

    def _capture_local_storage(self) -> Dict[str, str]:
        """Capture localStorage data"""
        try:
            return self.driver.execute_script("""
                var storage = {};
                for (var i = 0; i < localStorage.length; i++) {
                    var key = localStorage.key(i);
                    storage[key] = localStorage.getItem(key);
                }
                return storage;
            """)
        except:
            return {}

    def _capture_session_storage(self) -> Dict[str, str]:
        """Capture sessionStorage data"""
        try:
            return self.driver.execute_script("""
                var storage = {};
                for (var i = 0; i < sessionStorage.length; i++) {
                    var key = sessionStorage.key(i);
                    storage[key] = sessionStorage.getItem(key);
                }
                return storage;
            """)
        except:
            return {}

    def _capture_cookies(self) -> List[Dict[str, Any]]:
        """Capture all cookies"""
        try:
            return self.driver.get_cookies()
        except:
            return []

    def _capture_console_logs(self) -> List[Dict[str, str]]:
        """Capture browser console logs"""
        try:
            logs = self.driver.get_log('browser')
            return [{
                "level": log["level"],
                "message": log["message"],
                "timestamp": log["timestamp"]
            } for log in logs]
        except:
            return []

    def _capture_network_timing(self) -> Dict[str, float]:
        """Capture network performance timing"""
        try:
            return self.driver.execute_script("""
                var timing = performance.timing;
                return {
                    navigationStart: timing.navigationStart,
                    domainLookupStart: timing.domainLookupStart,
                    domainLookupEnd: timing.domainLookupEnd,
                    connectStart: timing.connectStart,
                    connectEnd: timing.connectEnd,
                    requestStart: timing.requestStart,
                    responseStart: timing.responseStart,
                    responseEnd: timing.responseEnd,
                    domLoading: timing.domLoading,
                    domInteractive: timing.domInteractive,
                    domContentLoadedEventStart: timing.domContentLoadedEventStart,
                    domContentLoadedEventEnd: timing.domContentLoadedEventEnd,
                    loadEventStart: timing.loadEventStart,
                    loadEventEnd: timing.loadEventEnd
                };
            """)
        except:
            return {}

    def _test_responsive_breakpoints(self) -> List[int]:
        """Test different screen sizes"""
        breakpoints = []
        sizes = [(1920, 1080), (1366, 768), (768, 1024), (414, 896), (375, 667)]
        
        try:
            current_size = self.driver.get_window_size()
            
            for width, height in sizes:
                self.driver.set_window_size(width, height)
                time.sleep(1)
                breakpoints.append(width)
            
            # Restore original size
            self.driver.set_window_size(current_size['width'], current_size['height'])
            
        except:
            pass
            
        return breakpoints

    def _analyze_accessibility(self) -> Dict[str, Any]:
        """Basic accessibility analysis"""
        try:
            return self.driver.execute_script("""
                var accessibility = {
                    images_without_alt: 0,
                    links_without_text: 0,
                    headings_structure: [],
                    form_labels: 0,
                    aria_labels: 0
                };
                
                // Images without alt text
                var imgs = document.querySelectorAll('img');
                imgs.forEach(function(img) {
                    if (!img.alt && !img.getAttribute('aria-label')) {
                        accessibility.images_without_alt++;
                    }
                });
                
                // Links without accessible text
                var links = document.querySelectorAll('a');
                links.forEach(function(link) {
                    if (!link.textContent.trim() && !link.getAttribute('aria-label')) {
                        accessibility.links_without_text++;
                    }
                });
                
                // Heading structure
                var headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                headings.forEach(function(h) {
                    accessibility.headings_structure.push({
                        level: h.tagName,
                        text: h.textContent.trim().substring(0, 50)
                    });
                });
                
                // Form labels
                accessibility.form_labels = document.querySelectorAll('label').length;
                
                // ARIA labels
                accessibility.aria_labels = document.querySelectorAll('[aria-label]').length;
                
                return accessibility;
            """)
        except:
            return {}

    def _analyze_seo(self) -> Dict[str, Any]:
        """Basic SEO analysis"""
        seo_info = {}
        
        try:
            seo_info = self.driver.execute_script("""
                var seo = {
                    title: document.title,
                    meta_description: '',
                    h1_count: document.querySelectorAll('h1').length,
                    h1_texts: [],
                    canonical_url: '',
                    og_tags: {},
                    twitter_tags: {},
                    structured_data: []
                };
                
                // Meta description
                var metaDesc = document.querySelector('meta[name="description"]');
                if (metaDesc) seo.meta_description = metaDesc.content;
                
                // H1 texts
                var h1s = document.querySelectorAll('h1');
                h1s.forEach(function(h1) {
                    seo.h1_texts.push(h1.textContent.trim());
                });
                
                // Canonical URL
                var canonical = document.querySelector('link[rel="canonical"]');
                if (canonical) seo.canonical_url = canonical.href;
                
                // Open Graph tags
                var ogTags = document.querySelectorAll('meta[property^="og:"]');
                ogTags.forEach(function(tag) {
                    seo.og_tags[tag.getAttribute('property')] = tag.content;
                });
                
                // Twitter tags
                var twitterTags = document.querySelectorAll('meta[name^="twitter:"]');
                twitterTags.forEach(function(tag) {
                    seo.twitter_tags[tag.getAttribute('name')] = tag.content;
                });
                
                // Structured data
                var scripts = document.querySelectorAll('script[type="application/ld+json"]');
                scripts.forEach(function(script) {
                    try {
                        seo.structured_data.push(JSON.parse(script.textContent));
                    } catch(e) {}
                });
                
                return seo;
            """)
        except:
            pass
            
        return seo_info

    def _save_page_analysis(self, url: str, analysis: PageAnalysis):
        """Save comprehensive page analysis"""
        slug = slugify_url(url)
        page_dir = self.out / "pages" / slug
        ensure_dir(page_dir)
        
        # Save the full analysis
        (page_dir / "analysis.json").write_text(
            json.dumps(asdict(analysis), indent=2, default=str), 
            encoding="utf-8"
        )
        
        # Save individual components for easier access
        if analysis.forms:
            (page_dir / "forms.json").write_text(
                json.dumps([asdict(f) for f in analysis.forms], indent=2), 
                encoding="utf-8"
            )
        
        if analysis.interactive_elements:
            (page_dir / "interactions.json").write_text(
                json.dumps([asdict(ie) for ie in analysis.interactive_elements], indent=2),
                encoding="utf-8"
            )
        
        if analysis.components:
            (page_dir / "components.json").write_text(
                json.dumps([asdict(c) for c in analysis.components], indent=2),
                encoding="utf-8"
            )

    def _write_comprehensive_output(self):
        """Write all collected data to files"""
        print("💾 Writing comprehensive analysis...")
        
        # Site map and basic summary
        (self.out / "site_map.json").write_text(
            json.dumps(sorted(self.site_map), indent=2), 
            encoding="utf-8"
        )
        
        # All API calls
        (self.out / "apis_comprehensive.json").write_text(
            json.dumps(self.api_store.to_list(), indent=2, default=str),
            encoding="utf-8"
        )
        
        # API calls by context
        for context in ["page_load", "user_interaction", "component_mount"]:
            context_apis = self.api_store.get_by_context(context)
            if context_apis:
                (self.out / f"apis_{context}.json").write_text(
                    json.dumps([asdict(api) for api in context_apis], indent=2, default=str),
                    encoding="utf-8"
                )
        
        # User flows
        if self.user_flows:
            (self.out / "user_flows.json").write_text(
                json.dumps(self.user_flows, indent=2, default=str),
                encoding="utf-8"
            )
        
        # Component analysis summary
        all_components = []
        for analysis in self.page_analyses.values():
            all_components.extend(analysis.components)
        
        if all_components:
            (self.out / "components_summary.json").write_text(
                json.dumps([asdict(c) for c in all_components], indent=2),
                encoding="utf-8"
            )
        
        # Forms summary
        all_forms = []
        for analysis in self.page_analyses.values():
            all_forms.extend(analysis.forms)
        
        if all_forms:
            (self.out / "forms_summary.json").write_text(
                json.dumps([asdict(f) for f in all_forms], indent=2),
                encoding="utf-8"
            )
        
        # Interactive elements summary
        all_interactions = []
        for analysis in self.page_analyses.values():
            all_interactions.extend(analysis.interactive_elements)
        
        if all_interactions:
            (self.out / "interactions_summary.json").write_text(
                json.dumps([asdict(i) for i in all_interactions], indent=2),
                encoding="utf-8"
            )
        
        # Technical summary
        tech_summary = {
            "base_url": self.base_url,
            "captured_at": now_iso(),
            "analysis_type": "comprehensive" if self.deep_analysis else "basic",
            "pages_crawled": len(self.visited),
            "pages_analyzed": len(self.page_analyses),
            "routes_found": len(self.site_map),
            "apis_detected": len(self.api_store.to_list()),
            "forms_found": len(all_forms),
            "components_found": len(all_components),
            "interactive_elements_found": len(all_interactions),
            "user_flows_tested": len(self.user_flows),
            "frameworks_detected": list(set(c.framework for c in all_components)),
            "pages_with_forms": len([a for a in self.page_analyses.values() if a.forms]),
            "pages_with_components": len([a for a in self.page_analyses.values() if a.components])
        }
        
        (self.out / "technical_summary.json").write_text(
            json.dumps(tech_summary, indent=2), 
            encoding="utf-8"
        )
        
        print(f"✅ Analysis complete! Results saved to {self.out}")
        print(f"📊 {tech_summary['pages_crawled']} pages crawled")
        print(f"🔍 {tech_summary['pages_analyzed']} pages deeply analyzed") 
        print(f"📡 {tech_summary['apis_detected']} API endpoints discovered")
        print(f"📝 {tech_summary['forms_found']} forms analyzed")
        print(f"🧩 {tech_summary['components_found']} components identified")
        print(f"🎯 {tech_summary['interactive_elements_found']} interactive elements mapped")

# ---------- CLI ----------

def parse_args():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", required=True, help="Base URL to crawl")
    ap.add_argument("--out", default="./dump_advanced", help="Output directory")
    ap.add_argument("--max-pages", type=int, default=50, help="Maximum pages to crawl")
    ap.add_argument("--deep", action="store_true", help="Enable deep analysis (slower but comprehensive)")
    ap.add_argument("--timeout", type=int, default=30, help="Page load timeout in seconds")
    ap.add_argument("--interaction-delay", type=float, default=1.0, help="Delay between interactions in seconds")
    return ap.parse_args()

def main():
    args = parse_args()
    
    print("🕷️  Advanced Site Crawler Starting...")
    print(f"🎯 Target: {args.url}")
    print(f"📁 Output: {args.out}")
    print(f"🔍 Deep Analysis: {'ON' if args.deep else 'OFF'}")
    
    crawler = AdvancedCrawler(
        base_url=args.url,
        out_dir=args.out, 
        max_pages=args.max_pages,
        deep_analysis=args.deep,
        nav_timeout=args.timeout,
        interaction_delay=args.interaction_delay
    )
    
    try:
        crawler.crawl()
    except KeyboardInterrupt:
        print("\n🛑 Crawling interrupted by user")
    except Exception as e:
        print(f"❌ Crawling failed: {e}")
        raise

if __name__ == "__main__":
    main()