# Content Integration Plan - Old Database to New Website

## Summary of Extracted Content

From the old WordPress database (`localhost.sql`), we successfully extracted:

- **212 Blog Posts** (2016-2022)
- **468 Pages** (various content)
- **15 Downloads** (PDFs and resources)
- **15 Consultant Profiles** (expert practitioners)

All extracted content is available in: `/Users/tuckerpeters/HabitsOfMind2/extracted_content/`

---

## 1. Consultant Profiles ✅ READY TO INTEGRATE

**Location:** `/frontend/src/routes/about/+page.svelte`

**Action Required:** Add 12 consultant profiles to the leadership team section

**Consultants to Add (already in leadership - skip these):**
- Art Costa ✓ (already exists)
- Bena Kallick ✓ (already exists)
- Allison Zmuda ✓ (already exists)

**New Consultants to Add (12 total):**
1. Michele De Bellis - Consultant
2. Karen-Tui Boyes - Founder of Spectrum Education
3. Catherine Caine - Educator at Waikiki School
4. Carol Hill, EdD - Director of Adult Education
5. Craig Gastauer - High School Instructional Leader
6. Juanita Henry - Consultant & Training Associate
7. Dana Lesperance - Head of School, Vermont
8. Liz Locatelli - Former ELA Teacher & Consultant
9. Pat Mullikin - Educational Consultant
10. Henry Toi - Founder of Nurture Craft
11. Daniel Vollrath - Special Education Teacher
12. Denise Washington - Career & College Consultant

**Formatted Code:** Available in `/Users/tuckerpeters/HabitsOfMind2/consultants_formatted.txt`

**Images Needed:** Placeholder images or actual photos at:
- `/frontend/static/images/team/[consultant-slug].jpg`

**Implementation Steps:**
1. Open `/frontend/src/routes/about/+page.svelte`
2. Find the `leadership` array (around line 10)
3. Add the 12 consultant profiles AFTER the existing 3 leaders
4. Add placeholder images or use default avatar images
5. Test the About page to ensure all profiles display correctly

---

## 2. Blog Posts (212 posts) - NEEDS REVIEW

**Current State:** Extracted to `/extracted_content/blog_posts.json` and `blog_posts.csv`

**Date Range:** 2016-2022

**Content Types:**
- Virtual school tours (YouTube embeds)
- Event announcements
- Webinar recordings
- Article releases
- Success stories

**Sample Posts:**
- "New eBook Release!" (2016)
- "Join Virtual Tours of IHOMCLE" (2016)
- "Leading Personalizing Learning: ASCD CEL 2016 Reflection" (2016)
- "Students at the Center: Personalized Learning with Habits of Mind" (2017)
- Multiple school tour videos (2017)

**Integration Options:**

### Option A: Import All to Firebase (Recommended)
Import blog posts into the existing Firebase blog system at `/frontend/src/routes/blog/`

**Pros:**
- Maintains historical content
- SEO benefits from old URLs
- Complete archive

**Cons:**
- 212 posts to review and clean
- May contain outdated links/images
- Some content may be redundant

**Steps:**
1. Review CSV file to identify valuable posts
2. Create import script for Firebase
3. Clean HTML content (remove old staging URLs)
4. Update image paths
5. Import in batches
6. Test blog listing and individual posts

### Option B: Selective Import
Only import highest-value posts (announcements, major events, key articles)

**Pros:**
- Curated, high-quality content
- Less cleanup work
- Focused message

**Cons:**
- Loses historical record
- May miss valuable content

---

## 3. Downloads (15 items) - REVIEW AGAINST EXISTING

**Current State:** Extracted to `/extracted_content/downloads.json`

**Action Required:** Cross-reference with existing resources in `/frontend/src/routes/resources/+page.svelte`

Many of these may already be in the new resources section. Need to:
1. Compare download titles with existing resources
2. Identify any missing downloads
3. Add missing downloads to resources page
4. Ensure PDFs are accessible in `/frontend/static/` or cloud storage

---

## 4. Pages (468 pages) - NEEDS DETAILED REVIEW

**Current State:** First 100 pages extracted to `/extracted_content/pages.json`

**Action Required:** Manual review to identify important missing pages

**Known Page Categories from Old Site:**
- Habit-specific pages (16 habits × multiple perspectives)
- Event pages
- Certification information
- Consulting services
- Historical content

**Review Process:**
1. Export page titles and slugs to CSV
2. Compare against new site structure
3. Identify critical missing pages
4. Prioritize for integration
5. Create new pages or add content to existing pages

**Key Pages to Check:**
- Individual habit descriptions (already exist - verify completeness)
- Certification process details
- Historical events/milestones
- Case studies
- Research articles

---

## Priority Integration Plan

### Phase 1: IMMEDIATE (This Session)
✅ 1. Add 12 consultant profiles to About page
   - Use formatted text in `consultants_formatted.txt`
   - Add placeholder images
   - Test About page

### Phase 2: SHORT TERM (Next Few Days)
2. Review blog posts CSV
   - Identify top 20-30 most valuable posts
   - Clean HTML content
   - Prepare for Firebase import

3. Cross-reference downloads
   - Compare with existing resources
   - Identify gaps
   - Add missing items

### Phase 3: MEDIUM TERM (Next Week)
4. Review pages extraction
   - Extract all 468 page titles
   - Create comparison matrix
   - Identify critical missing content

5. Import selected blog posts
   - Create Firebase import script
   - Batch import cleaned posts
   - Test blog functionality

### Phase 4: LONG TERM (Ongoing)
6. Import additional blog posts
   - Continue cleaning and importing
   - Build complete archive

7. Integrate missing pages
   - Create new pages as needed
   - Enhance existing pages with old content

---

## Technical Notes

### Extracted Files Location
```
/Users/tuckerpeters/HabitsOfMind2/extracted_content/
├── blog_posts.json      (212 posts with full content)
├── blog_posts.csv       (212 posts summary for easy review)
├── pages.json           (100 pages sample)
├── downloads.json       (15 downloads)
└── consultants.json     (15 consultant profiles)
```

### Helper Scripts
```
/Users/tuckerpeters/HabitsOfMind2/
├── parse_old_database.py         (Initial extraction)
├── extract_full_content.py       (Full content extraction)
├── format_consultants.py         (Format for About page)
└── consultants_formatted.txt     (Ready-to-use consultant code)
```

### Image Requirements
Consultant photos needed at:
```
/frontend/static/images/team/michele-de-bellis.jpg
/frontend/static/images/team/karen-tui-boyes.jpg
/frontend/static/images/team/catherine-caine.jpg
/frontend/static/images/team/carol-hill-edd.jpg
/frontend/static/images/team/craig-gastauer.jpg
/frontend/static/images/team/juanita-henry.jpg
/frontend/static/images/team/dana-lesperance.jpg
/frontend/static/images/team/liz-locatelli-ed-d.jpg
/frontend/static/images/team/pat-mullikin.jpg
/frontend/static/images/team/henry-toi.jpg
/frontend/static/images/team/daniel-vollrath.jpg
/frontend/static/images/team/denise-washington.jpg
```

---

## Next Steps

**Immediate Action (Now):**
1. Integrate 12 consultant profiles into About page
2. Add placeholder images or use default avatars

**User Decision Needed:**
- Do you want to import ALL 212 blog posts or be selective?
- Do you have actual photos for the consultants or should we use placeholders?
- Are there specific pages from the old site you know are missing?

**Questions to Answer:**
1. Do you have access to the old images/photos from the WordPress media library?
2. Should we preserve old URLs for SEO (redirects)?
3. What's the priority - complete archive or curated content?
