# Merge View - User Guide

## Overview

The Merge View is where you process incoming documents. This is the main screen you'll use daily to:
- Match incoming files to documents in your database
- Record revision information
- Review matching status before processing
- Merge files into their final locations

Think of this view as your document processing workbench. All the settings you configured earlier come together here to help you quickly process batches of documents.

This guide covers how to use the Revision Information section and understand the Document Matching Results.

---

## Recording Revision Information

Before processing documents, you need to provide two pieces of information about the revision batch:

### Revision Date

**Description:** The official date for this revision batch. This date is saved with each document's revision history and represents when the documents were issued or submitted.

**Type:** Date picker

**Sample Values:**
- `2024-01-15` - For a January 15, 2024 issue
- `2024-03-10` - For a March 10, 2024 submission
- Today's date - For documents being issued today

**Requirements:**
- Must select a date before you can merge documents
- Cannot be empty
- Date format displays based on your computer's regional settings

**What This Date Represents:**
- The date you issued drawings for construction
- The date documents were submitted to the client
- The date of a planning submission
- Any other significant milestone date

**How to Use It:**

1. Click on the date picker control
2. A calendar pops up
3. Navigate to the month and year you need
4. Click the date to select it
5. The selected date appears in the control

**Usage Notes:**
- Use the date from your project transmittal or cover sheet
- Be consistent - decide if you're using issue dates, approval dates, etc., and stick with it
- The "Merge Documents" button remains disabled until you select a date

---

### Revision Description

**Description:** A brief explanation of what this revision is for. This helps you and others understand the purpose of the revision when looking at document history later.

**Type:** Text field with autocomplete suggestions

**Sample Values:**
- `Issued for Construction` - Documents released to contractors for building
- `Client Comments Incorporated` - Revisions based on client feedback
- `Planning Submission` - Documents submitted for planning approval
- `Reissued - Contractor Queries Answered` - Updated documents responding to questions
- `Tender Issue` - Documents released for bidding

**Requirements:**
- Must enter a description before you can merge documents
- Cannot be empty
- Can be any text that describes the revision purpose

**The Smart Suggestions Feature:**

As you type, the application searches through descriptions you've used before and shows matching suggestions. This helps keep your descriptions consistent.

**How It Works:**
1. Click in the text box
2. Start typing your description
3. Suggestions appear below the box as you type
4. Click a suggestion to use it, or keep typing your own
5. Press Enter or click elsewhere to confirm your entry

**Example:**
- You type: "Issued"
- You see suggestions like:
  - Issued for Construction
  - Issued for Tender
  - Issued for Approval
- Click one to use it, or keep typing your own description

**Why This Helps:**
- Keeps your descriptions consistent across revisions
- Saves typing time for common descriptions
- Reduces typos and spelling errors
- Helps you remember the exact wording you used before
- Makes it easier to find specific revisions later

**Good Description Examples:**
- `Issued for Construction` - Clear purpose
- `Client Comments Incorporated` - Explains what changed
- `Planning Submission` - Indicates destination
- `Reissued - Contractor Queries Answered` - Explains why it's being reissued

**Avoid Vague Descriptions:**
- `Updates` ❌ - Too vague (What updates?)
- `Changes` ❌ - Too general (What changed?)
- `Version 2` ❌ - Unclear (Why version 2?)
- `Rev B` ❌ - Redundant (revision code is already tracked separately)

**Usage Notes:**
- The "Merge Documents" button remains disabled until you enter a description
- Suggestions only appear if you've used similar descriptions before
- You're not limited to suggestions - you can type anything you want

---

### Ready to Merge?

The "Merge Documents" button will only become active (clickable) when you've provided both pieces of information:

âœ“ **Revision Date** - Selected from the date picker
âœ“ **Revision Description** - Entered in the text box

If the button is grayed out, check that you've filled in both fields.

**Note:** The button also requires that your database is connected and the system isn't busy processing something else.

---

## Understanding Your Document Matching Results

After the application scans your incoming folder, it shows you a list of all files it found and whether it could match each one to a document in your database. This section helps you understand what you're looking at and what actions you might need to take.

The results appear in a table in the middle of the screen, with a summary bar at the top and action buttons at the bottom.

---

### The Summary Bar (At the Top)

At the top of the results table, you'll see a summary that gives you a quick overview:

**Total:** How many files were found in your incoming folder

**Matched:** How many files were successfully matched and are ready to process (shown in green)

**Warnings:** How many files have minor issues but can still be processed (shown in orange)

**No Match:** How many files couldn't be matched or have errors that need fixing (shown in red)

**Example:**
```
Total: 25 | Matched: 18 | Warnings: 3 | No Match: 4
```

This tells you that out of 25 files, 18 are good to go, 3 have warnings you should be aware of, and 4 need attention before they can be processed.

---

### The Results Table

Below the summary, you'll see a table with one row for each file found in your incoming folder. The table has alternating white and light gray rows to make it easier to read.

Here's what each column tells you:

#### Status (Colored Circle)

This column shows a colored circle that quickly tells you the status of each file:

**ðŸŸ¢ Green Circle - All Good**
- The file was successfully matched to a document in your database
- The revision is the next logical step from what's currently in the database
- You can merge this file without any concerns
- Hover your mouse over the circle to see more details

**ðŸŸ  Orange Circle - Warning**
- The file was matched to a document, but there's something to be aware of
- Usually means the revision isn't sequential (for example, going from revision B to revision D, skipping C)
- You CAN still merge these files - the warning just alerts you to check if this is intentional
- Hover over the circle to see exactly what the issue is

**ðŸ”´ Red Circle - Error (Needs Attention)**
- Something is preventing this file from being processed
- There are three types of red circle errors:

1. **Missing Revision Information**
   - The application couldn't find revision information in the filename
   - Check that your filename includes the revision markers you configured in Settings
   - Example error: "No revision information found in filename"

2. **Duplicate Document**
   - You have multiple files of the same type trying to match the same document
   - For example: Two PDFs both trying to match document ABC-001
   - Remove the duplicate or process files separately
   - The error message will list all the duplicate filenames

3. **No Match Found**
   - The application couldn't find a matching document in your database
   - The document number in the filename doesn't exist in your database
   - Use the "Add New Documents" button to add it, or check if the filename format is correct

**Tip:** Always hover your mouse over the colored circle to see the full explanation.

#### Incoming File

Shows the name of the file in your incoming folder.

**Example:** `ABC-001-Rev-A.pdf`

This is just the filename, not the full path to where it's stored.

#### Incoming Rev

Shows the revision code that was extracted from the filename.

**Examples:**
- `A`, `B`, `C` (letter revisions)
- `01`, `02`, `03` (number revisions)
- `P01`, `P02` (prefixed revisions)

**If blank:** The application couldn't find revision information in the filename, which will cause a red error status.

#### Matched Doc #

Shows the document number from your database that the file matched to.

**Example:** `ABC-001`

**If blank:** No matching document was found in your database (red "No Match Found" error).

#### Matched Doc Name

Shows the document name/title from your database. This helps you confirm the right document was matched.

**Example:** `Ground Floor Plan`

**If blank:** No match was found.

#### Current Rev

Shows the current revision of the matched document in your database.

**Example:** If the database shows revision `B` and your incoming file is revision `C`, you'll see:
- Incoming Rev: `C`
- Current Rev: `B`
- Status: Green (C follows B)

If your incoming file skipped a revision (like going from `B` to `D`), you'll see an orange warning.

#### Status Message

A plain-English explanation of what's happening with this file.

**Examples you might see:**

**Green Status:**
- "Match OK - Sequential revision"
- "Match found"

**Orange Warning:**
- "Warning - Revision not sequential (Current: A, Incoming: C)"
  - This means the database shows revision A, but your incoming file is revision C (skipping B)

**Red Errors:**
- "ERROR - No revision information found in filename (blocks merge)"
  - Check your filename format and Settings configuration
  
- "ERROR - Duplicate document (blocks merge). Same file type matched to document ABC-001. Duplicates: ABC-001-A.pdf, ABC-001-A-Copy.pdf"
  - Multiple files are trying to match the same document - remove duplicates

- "No match found"
  - This document number isn't in your database

---

### Action Buttons (At the Bottom)

At the bottom of the results table, you'll find two buttons:

#### Refresh Button

**What it does:** Scans your incoming folder again and updates all the matching results.

**When to use it:**
- After you've added or removed files from your incoming folder
- After you've changed settings (like revision markers or filing rules)
- After you've added documents to your database
- When you want to see the current state of files

**How it works:**
1. Click the Refresh button
2. The application scans your incoming folder
3. It matches each file against your current database
4. The table updates with the latest results
5. You'll see a message at the top summarizing the results

**What gets checked:**
- Which files are in the incoming folder
- Whether each file matches a document in the database
- Whether revisions are sequential
- Whether there are any duplicate files

**How long it takes:** Usually just a few seconds, depending on how many files you have.

#### Add New Documents Button

This button opens a dialog that helps you add unmatched files to your database as new documents. It's covered in a separate section of the documentation.

---

## Understanding Status Priority

When the application checks a file, it can find multiple issues. But it only shows you one status per file - the most important issue.

Here's the order of importance (most serious first):

1. **ðŸ”´ Missing Revision** (Most Serious)
   - If a file has no revision information, this error shows up first
   - Even if the file matches a document, the missing revision is the critical problem

2. **ðŸ”´ Duplicate Document**
   - If you have multiple files of the same type for the same document
   - Only checked if the file has revision information

3. **ðŸ”´ No Match**
   - The document number isn't in your database

4. **ðŸŸ  Revision Not Sequential**
   - The file matches, but the revision skips a number
   - This is just a warning - you can still merge

5. **ðŸŸ¢ All Good** (Least Serious)
   - Everything checks out fine

### Why This Matters

**Example:** Imagine you have a file called `ABC-001.pdf` (no revision in the name).
- The document ABC-001 exists in your database
- But you'll still see a red "Missing Revision" error
- That's because missing revision is more important than whether it matched

**Another Example:** You have two files: `ABC-001-Rev-A.pdf` and `ABC-001-Rev-A-Copy.pdf`
- Both are PDFs trying to match document ABC-001
- You'll see a red "Duplicate Document" error
- The application can't tell which one is the right file to use

---

## How Revision Sequencing Works

The application checks if your incoming revision is the "next" logical revision after what's currently in the database.

### For Letter Revisions (A, B, C...)

**Sequential means:** The next letter in the alphabet

**Examples:**
- Current: A, Incoming: B â†’ âœ“ Sequential (green)
- Current: A, Incoming: C â†’ âœ— Not Sequential (orange warning)
- Current: B, Incoming: C â†’ âœ“ Sequential (green)

### For Number Revisions (1, 2, 3... or 01, 02, 03...)

**Sequential means:** The next number in sequence

**Examples:**
- Current: 5, Incoming: 6 â†’ âœ“ Sequential (green)
- Current: 5, Incoming: 7 â†’ âœ— Not Sequential (orange warning)
- Current: 01, Incoming: 02 â†’ âœ“ Sequential (green)

### For Other Revision Schemes (P01, Rev-A, etc.)

For more complex revision numbering, the application currently accepts any incoming revision without a warning. This can be customized based on your specific needs.

### If the Database Has No Current Revision

If a document in your database doesn't have a revision yet (the revision field is blank), any incoming revision is accepted as OK.

---

## When Does the List Update?

The list of files and their matching status updates automatically in these situations:

**You click the Refresh button:** This is the manual way to update the list whenever you want.

**After you add new documents:** When you use the "Add New Documents" button and successfully add documents to the database, the list automatically refreshes to show you the new matches.

**After you merge documents:** Once the merge process completes, the list refreshes to show you which files are still in the incoming folder.

**Tip:** If you add or remove files from your incoming folder outside the application (using Windows Explorer, for example), click the Refresh button to see the changes.

---

## Working with the Results

### Getting More Information

**Hover over colored circles:** Move your mouse over any colored status circle to see a tooltip with detailed information about that file's status.

**Click a row:** You can click on any row to select it. The row will be highlighted.

**Scroll through results:** If you have many files, use the scrollbar on the right or your mouse wheel to scroll through the list.

### What You Can Do

**Review the results:** Look through the list to see which files are ready (green), which have warnings (orange), and which need attention (red).

**Fix issues:** Based on what you see, you might need to:
- Remove duplicate files from your incoming folder
- Check that filenames have revision information
- Add missing documents to your database

**Refresh when needed:** After making changes, click the Refresh button to see updated results.

**Add new documents:** If you have files with "No match found," you can add them to your database using the "Add New Documents" button.

**Proceed with merge:** Once you're satisfied with the results and have entered revision information, click the "Merge Documents" button.

---

## Messages You'll See

At the top of the screen, you'll see messages that tell you what's happening:

**Blue/Gray Messages:** General information (auto-disappears after a few seconds)
- "Successfully matched 18 documents. 3 warnings."
- "Refresh completed."

**Orange/Yellow Messages:** Warnings that need your attention (stay visible longer)
- "Document matching completed with issues. 15 can be merged, 3 warnings. Errors: 2 missing revision, 1 duplicate, 4 no match."

**Red Messages:** Errors that need to be fixed (stay visible until you dismiss them)
- "Error during document matching: [details of what went wrong]"

---

## Tips for Success

### Before You Start

**Check Your Settings:**
- Make sure your incoming folder path is correct
- Verify your revision markers (prefix and suffix) match your file naming
- Confirm your filing rules are set up correctly
- Make sure all the file types you use are listed in supported file types

**Check Your Database:**
- Ensure your database is connected
- Verify the documents in your database are up to date

### Reading the Results

**Green Circles (All Good):**
- Double-check the matched document number is what you expect
- Verify the revision makes sense (going from A to B, 1 to 2, etc.)
- These files are ready to process

**Orange Circles (Warning):**
- Read the warning message to understand what's not sequential
- Decide if the revision jump is intentional (sometimes you skip revisions)
- These files CAN still be merged - the warning is just alerting you
- If it's a mistake, you may want to fix it before merging

**Red Circles (Error):**
- **Missing Revision:** Check your filename includes the revision markers
- **Duplicate:** Remove extra copies of files or rename them
- **No Match:** Either add the document to your database or check if the filename is correct

### Handling Common Situations

**Processing Many Files at Once:**
- Look at the summary numbers first to get an overview
- Focus on fixing red errors before anything else
- Deal with duplicates first, then missing revisions, then no matches

**Frequent Orange Warnings:**
- If you often skip revisions (like going from A to C), this is normal
- The warnings are just making sure you're aware
- You can still merge - just make sure it's intentional

**Lots of "No Match Found" Errors:**
- This usually means you have new documents that aren't in your database yet
- Use the "Add New Documents" button to add them in a batch
- Or double-check that your filing rules are extracting document numbers correctly

---

## Troubleshooting Common Problems

### Problem: No files showing up

**What you see:** The table is empty, Total count shows 0

**What to check:**
- Is your incoming folder path correct? (Check in Settings)
- Are there actually files in that folder?
- Do the files have file extensions you've set up as supported? (Check Settings)
- Can you open the folder in Windows Explorer?

### Problem: Everything shows "No match found"

**What you see:** All files have red circles with "No match found"

**What to check:**
- Is your database connected?
- Does your database actually have documents in it?
- Are your filing rules extracting the document numbers correctly from filenames?
- Try testing with one file you know should match

### Problem: Everything shows "Missing Revision"

**What you see:** All files have red circles saying "ERROR - No revision information found"

**What to check:**
- Do your filenames actually include revision information?
- Are the revision prefix and suffix in Settings correct?
- Does the prefix and suffix match exactly what's in your filenames?
- Example: If your files look like `ABC-001-Rev-A.pdf`, your prefix should be `Rev-` and suffix should be something like `.pdf`

### Problem: Many duplicate file errors

**What you see:** Multiple files showing "ERROR - Duplicate document"

**What to check:**
- Do you have actual duplicate files in your incoming folder?
- Look for files with names like `Document(1).pdf` or `Document-Copy.pdf`
- Remove or rename the duplicates

### Problem: The Refresh button doesn't work

**What you see:** Nothing happens when you click Refresh

**What to check:**
- Is the system busy? (The button might be grayed out)
- Is your database still connected?
- Look for error messages at the top of the screen
- Try closing and reopening the application

### Problem: The counts don't add up

**What you see:** Matched + Warnings + No Match doesn't equal Total

**This is normal!** The "No Match" count includes all the red errors (missing revision, duplicates, and actual no matches). Some categories overlap.

---

## How Long Does Refresh Take?

The Refresh operation is usually pretty quick:

- **Few files (under 100):** Less than a second
- **Medium batch (100-500):** A few seconds
- **Large batch (500-1000):** 5-15 seconds
- **Very large batch (over 1000):** 15-30 seconds or more

**What affects speed:**
- How many files are in your incoming folder
- How many documents are in your database
- How complex your filing rules are

**Tip:** Keep your incoming folder organized. After processing files, move them out or archive them so the folder doesn't get too full.

---

## How This Connects to Other Features

### Settings You've Already Configured

Everything you see in the Merge View comes from settings you configured earlier:

**From Current Folder Settings:**
- **Incoming Folder Path:** Where the application looks for files
- **Revision Prefix/Suffix:** How the application finds revision information in filenames
- **Filing Rules:** How the application figures out document numbers from filenames
- **Supported File Types:** Which files the application processes

**From Database Settings:**
- **Documents:** The list of documents that incoming files are matched against
- **Current Revisions:** What the incoming revisions are compared to

### What Happens When You Click "Merge Documents"

Once you've reviewed the results and entered revision information, clicking "Merge Documents" will:

1. Update your database with the new revision information
2. Move files to their final locations based on your filing rules
3. Export metadata if you have cloud integration enabled
4. Give you a summary of what was processed

This is covered in more detail in separate documentation about the merge process.

---

## Quick Reference

### Status Colors at a Glance

ðŸŸ¢ **Green** = All good, ready to merge
ðŸŸ  **Orange** = Warning, can still merge but be aware
ðŸ”´ **Red** = Error, needs to be fixed before merging

### Common Error Messages

| Message | What It Means | What To Do |
|---------|---------------|------------|
| No match found | Document number not in database | Use "Add New Documents" or check filename |
| ERROR - No revision information found | Filename doesn't have revision markers | Check filename format and Settings |
| ERROR - Duplicate document | Multiple files for same document+type | Remove duplicate files |
| Warning - Revision not sequential | Revision skips a number/letter | Verify this is intentional, can still merge |

### Before You Merge Checklist

- [ ] Review all red errors and fix them
- [ ] Check orange warnings and confirm they're OK
- [ ] Verify green matches look correct
- [ ] Enter Revision Date
- [ ] Enter Revision Description
- [ ] Click "Merge Documents" when ready
