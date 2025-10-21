#!/usr/bin/env node

/**
 * Consultant Information Extractor
 *
 * This script extracts consultant and team member information from
 * the Institute for Habits of Mind website to populate the about page.
 */

const fs = require('fs');
const path = require('path');

// Function to extract consultant information from scraped content
function extractConsultantsFromContent(htmlContent) {
  const consultants = [];

  // Patterns to match consultant information
  const patterns = {
    // Email pattern
    email: /([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g,
    // Name patterns (common title prefixes)
    name: /(?:Dr\.|Professor|Mr\.|Ms\.|Mrs\.)\s+([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)/g,
    // Phone numbers
    phone: /(\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})/g,
    // Professional titles
    titles: /(?:consultant|educator|teacher|principal|director|coordinator|specialist|expert|trainer|facilitator)/gi
  };

  // Extract emails
  const emails = [...htmlContent.matchAll(patterns.email)].map(match => match[1]);

  // Extract names with titles
  const names = [...htmlContent.matchAll(patterns.name)].map(match => match[1]);

  // Extract phone numbers
  const phones = [...htmlContent.matchAll(patterns.phone)].map(match => match[1]);

  return {
    emails: [...new Set(emails)],
    names: [...new Set(names)],
    phones: [...new Set(phones)]
  };
}

// Function to extract team/staff information from specific pages
function extractTeamInformation(htmlContent) {
  const teamMembers = [];

  // Look for team/staff sections
  const teamSectionRegex = /<(?:div|section)[^>]*(?:class|id)="[^"]*(?:team|staff|about|bio)[^"]*"[^>]*>(.*?)<\/(?:div|section)>/gis;

  const teamSections = [...htmlContent.matchAll(teamSectionRegex)];

  teamSections.forEach(section => {
    const sectionContent = section[1];

    // Extract structured information from team sections
    const memberInfo = extractConsultantsFromContent(sectionContent);

    // Look for bio information
    const bioPattern = /<p[^>]*class="[^"]*bio[^"]*"[^>]*>(.*?)<\/p>/gis;
    const bios = [...sectionContent.matchAll(bioPattern)].map(match =>
      match[1].replace(/<[^>]*>/g, '').trim()
    );

    if (memberInfo.names.length > 0 || memberInfo.emails.length > 0) {
      teamMembers.push({
        ...memberInfo,
        bios,
        section: 'team'
      });
    }
  });

  return teamMembers;
}

// Process HTTrack scraped content
async function processScrapedContent() {
  const httrackPath = path.join(__dirname, '..', 'habitsofmind_httrack');
  const dumpPath = path.join(__dirname, '..', 'dump');

  let contentPath = null;
  if (fs.existsSync(httrackPath)) {
    contentPath = httrackPath;
    console.log('🔍 Found HTTrack directory, processing...');
  } else if (fs.existsSync(dumpPath)) {
    contentPath = dumpPath;
    console.log('🔍 Found dump directory, processing...');
  } else {
    console.log('❌ No scraped content directory found. Please ensure the website has been scraped.');
    return null;
  }

  console.log('🔍 Processing scraped content for consultant information...');

  // Get HTML files from the content directory
  let files = [];
  if (contentPath === httrackPath) {
    files = fs.readdirSync(contentPath).filter(file => file.endsWith('.html'));
  } else {
    // For dump directory, search recursively for HTML files
    function findHtmlFiles(dir) {
      const htmlFiles = [];
      const entries = fs.readdirSync(dir, { withFileTypes: true });

      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        if (entry.isDirectory()) {
          htmlFiles.push(...findHtmlFiles(fullPath));
        } else if (entry.name.endsWith('.html')) {
          htmlFiles.push(fullPath);
        }
      }
      return htmlFiles;
    }

    const htmlPaths = findHtmlFiles(contentPath);
    files = htmlPaths.map(p => ({ path: p, name: path.basename(p) }));
  }
  const consultantData = {
    emails: new Set(),
    names: new Set(),
    phones: new Set(),
    teamMembers: [],
    consultants: []
  };

  let processedCount = 0;

  // Priority files to check first (likely to contain team info)
  let priorityFiles, otherFiles, filesToProcess;

  if (contentPath === httrackPath) {
    priorityFiles = files.filter(file =>
      file.toLowerCase().includes('about') ||
      file.toLowerCase().includes('team') ||
      file.toLowerCase().includes('staff') ||
      file.toLowerCase().includes('consultant') ||
      file.toLowerCase().includes('contact')
    );
    otherFiles = files.filter(file => !priorityFiles.includes(file));
    filesToProcess = [...priorityFiles, ...otherFiles];
  } else {
    // For dump directory structure
    priorityFiles = files.filter(file => {
      const fileName = typeof file === 'string' ? file : file.name;
      return fileName.toLowerCase().includes('about') ||
        fileName.toLowerCase().includes('team') ||
        fileName.toLowerCase().includes('staff') ||
        fileName.toLowerCase().includes('consultant') ||
        fileName.toLowerCase().includes('contact');
    });
    otherFiles = files.filter(file => !priorityFiles.includes(file));
    filesToProcess = [...priorityFiles, ...otherFiles];
  }

  for (const file of filesToProcess.slice(0, 20)) { // Limit to first 20 files
    try {
      let filePath, fileName;
      if (typeof file === 'string') {
        filePath = path.join(contentPath, file);
        fileName = file;
      } else {
        filePath = file.path;
        fileName = file.name;
      }

      const htmlContent = fs.readFileSync(filePath, 'utf8');

      // Extract consultant information
      const extracted = extractConsultantsFromContent(htmlContent);

      // Add to master sets
      extracted.emails.forEach(email => consultantData.emails.add(email));
      extracted.names.forEach(name => consultantData.names.add(name));
      extracted.phones.forEach(phone => consultantData.phones.add(phone));

      // Extract team-specific information
      if (priorityFiles.includes(file)) {
        const teamInfo = extractTeamInformation(htmlContent);
        consultantData.teamMembers.push(...teamInfo);
      }

      processedCount++;

      if (processedCount % 10 === 0) {
        console.log(`✓ Processed ${processedCount} files...`);
      }

    } catch (error) {
      console.error(`❌ Error processing ${fileName}:`, error.message);
    }
  }

  // Convert sets back to arrays
  consultantData.emails = Array.from(consultantData.emails);
  consultantData.names = Array.from(consultantData.names);
  consultantData.phones = Array.from(consultantData.phones);

  return consultantData;
}

// Generate consultant data for the about page
function generateConsultantData(extractedData) {
  if (!extractedData) return null;

  // Create consultant objects by matching names with emails/phones where possible
  const consultants = [];

  // Try to match names with emails (basic heuristic)
  extractedData.names.forEach(name => {
    const nameParts = name.toLowerCase().split(' ');
    const firstName = nameParts[0];
    const lastName = nameParts[nameParts.length - 1];

    // Look for matching email patterns
    const matchingEmail = extractedData.emails.find(email => {
      const emailLower = email.toLowerCase();
      return emailLower.includes(firstName) || emailLower.includes(lastName);
    });

    consultants.push({
      name,
      email: matchingEmail || null,
      title: 'Consultant', // Default title
      region: 'Unknown', // To be categorized later
      specialization: null
    });
  });

  // Add emails without matched names as separate entries
  const matchedEmails = consultants.map(c => c.email).filter(Boolean);
  const unmatchedEmails = extractedData.emails.filter(email => !matchedEmails.includes(email));

  unmatchedEmails.forEach(email => {
    consultants.push({
      name: email.split('@')[0].replace(/[._]/g, ' '), // Generate name from email
      email,
      title: 'Consultant',
      region: 'Unknown',
      specialization: null
    });
  });

  return {
    consultants: consultants.slice(0, 50), // Limit to first 50
    summary: {
      totalEmails: extractedData.emails.length,
      totalNames: extractedData.names.length,
      totalPhones: extractedData.phones.length,
      teamMembers: extractedData.teamMembers.length
    }
  };
}

// Main execution
async function main() {
  try {
    console.log('🚀 Starting consultant information extraction...');

    // Process scraped content
    const extractedData = await processScrapedContent();

    if (!extractedData) {
      console.log('⚠️ No data could be extracted. Please ensure the website has been scraped.');
      return;
    }

    // Generate consultant data
    const consultantData = generateConsultantData(extractedData);

    if (!consultantData) {
      console.log('❌ Failed to generate consultant data.');
      return;
    }

    // Save results
    const outputPath = path.join(__dirname, '..', 'frontend', 'src', 'lib', 'consultantData.json');
    fs.writeFileSync(outputPath, JSON.stringify(consultantData, null, 2));

    console.log(`\n✅ Successfully extracted consultant information:`);
    console.log(`   📧 Emails found: ${consultantData.summary.totalEmails}`);
    console.log(`   👤 Names found: ${consultantData.summary.totalNames}`);
    console.log(`   📞 Phones found: ${consultantData.summary.totalPhones}`);
    console.log(`   👥 Team members: ${consultantData.summary.teamMembers}`);
    console.log(`   🎯 Consultants processed: ${consultantData.consultants.length}`);
    console.log(`\n💾 Data saved to: ${outputPath}`);

    // Generate summary for manual review
    console.log('\n📋 Sample extracted consultants:');
    consultantData.consultants.slice(0, 10).forEach((consultant, index) => {
      console.log(`   ${index + 1}. ${consultant.name}${consultant.email ? ` (${consultant.email})` : ''}`);
    });

    if (consultantData.consultants.length > 10) {
      console.log(`   ... and ${consultantData.consultants.length - 10} more`);
    }

  } catch (error) {
    console.error('❌ Error in main execution:', error);
  }
}

if (require.main === module) {
  main();
}

module.exports = {
  extractConsultantsFromContent,
  extractTeamInformation,
  processScrapedContent,
  generateConsultantData
};