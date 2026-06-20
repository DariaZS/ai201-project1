# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |
| 7 | | | |
| 8 | | | |
| 9 | | | |
| 10 | | | |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**

**Overlap:**

**Why these choices fit your documents:**

**Final chunk count:**

---

## Sample Chunks

<!-- Paste 5 representative chunks from your document collection after running your ingestion pipeline.
     For each chunk, note which source document it came from.
     These must be actual text — not screenshots. -->

| # | Source document | Chunk text |
|---|----------------|------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Sample Chunks

| # | Source document | Chunk text |
|---|----------------|------------|
| 1 | cs_faq.txt | FAQ for Currently Enrolled Undergraduates \| Department of Computer Science, Columbia University. Have a question or concern about your program? You're in the right place! GENERAL ADVISING & MAJOR DECLARATION When can I declare CS as my major? |
| 2 | cs_faq.txt | When can I declare CS as my major? Are there any minimum requirements that I need to meet before declaring the major? The major declaration period occurs during your sophomore year: in the fall semester for SEAS students and the spring semester for Columbia College, GS, and Barnard students. |
| 3 | bwog_housing_strategy.txt | The only way to bring up your lottery number is to have rising junior(s) in your group, as they have a higher point value. Lottery numbers are otherwise randomly generated within your lottery number range. All beds in an apartment or double must be filled in order to select into a space. |
| 4 | ods_registration.txt | Disability Services reviews each request and determines eligibility for accommodations and services. The review process does not begin until your completed registration form and your disability documentation are received. The review process takes approximately three weeks. |
| 5 | dining_halls_guide.txt | John Jay - Biggest, decent selection, has meatless mondays (which is tragic imo). JJ's Diner - Smallest, is basically just junk food, is open very late. Ferris Booth Commons - Generally has the nicest food, always decently busy. |

**Total chunk count: 201 chunks across 10 documents.**

This falls comfortably within the healthy range (more than 50, less than 2,000), indicating chunk size is reasonable — not so large that topics get diluted, not so small that individual chunks lose meaning.

Each chunk above is a complete, self-contained thought ending on a real sentence boundary. My first implementation used raw character-count slicing, which cut chunks mid-word (e.g., "Are ther" instead of "Are there"). I rewrote `chunk_text()` to group whole sentences instead, fixing this issue.

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

---

## Retrieval Test Results

**Query 1:** How does the Columbia housing lottery actually work?

Top returned chunks:
- (source: bwog_housing_strategy, distance: 0.381) "Columbia Housing Strategy For Rising Sophomores. Housing can be stressful. Between navigating housing groups to understanding just how the housing lottery works, it can be overwhelming, especially as a rising sophomore..."
- (source: housing_lottery_points, distance: 0.449) "Every group member receives the same lottery number. Students will receive an email when lottery numbers are posted in the Housing Portal. Appointment Times: Each individual or group is then assigned a specific appointment date and time..."
- (source: housing_lottery_points, distance: 0.500) "Lottery numbers determine the order of Room Selection appointments. Students with higher class standing have a higher point value and are assigned a lower lottery number and an earlier Room Selection appointment time..."

Relevance explanation: All three top results directly explain how the lottery mechanism works — point values determining lottery number ranges, and lottery numbers determining appointment order. The top result blends official process information with student-written framing, while results 2 and 3 come from the official Columbia Housing point-values page. Together they would let an LLM construct an accurate, well-sourced answer.

---

**Query 2:** What is the best dining hall at Columbia?

Top returned chunks:
- (source: dining_halls_guide, distance: 0.272) "There are several themed dinners hosted by Columbia Dining throughout the year, such as French Night, Taste of the Caribbean, Campout... There is also the Battle of the Dining Halls, a friendly competition..."
- (source: dining_halls_guide, distance: 0.330) "Dining locations on Columbia's main campus include Blue Java Cafe at Butler Library, Mudd Hall, and Uris Hall; Lenfest Cafe in Jerome Greene Hall; The Fac Shack near the John Jay gates; Ferris Booth Commons..."
- (source: dining_halls_guide, distance: 0.337) "Your Guide to the Best Dining Halls at Columbia. Eating on campus is a convenient way to consume a delicious variety of foods and meals from different cuisines..."

Relevance explanation: All three results come from the dedicated dining halls guide and describe dining hall features, events, and locations — directly relevant to a "best dining hall" question. None of the results pull from an unrelated source, which confirms the embedding model is correctly distinguishing dining content from the other 9 sources in the corpus.

---

**Query 3:** How do I register for disability accommodations at Columbia?

Top returned chunks:
- (source: ods_registration, distance: 0.188) "Who is eligible? Any Columbia student with a disability or temporary injury on the Morningside, Manhattanville, and Medical campuses is eligible to submit requests for academic or campus accommodations from Disability Services..."
- (source: ods_registration, distance: 0.193) "Register with Disability Services - Columbia Health. Columbia Health provides Disability Accommodations for students registered with Disability Services (DS)..."
- (source: spectator_ods_guide, distance: 0.258) "Although Disability Services provides a step-by-step breakdown on how to register, Spectrum is here to help you with the process by simplifying it even further..."

Relevance explanation: This query produced the strongest retrieval of all three tests, with the top result scoring 0.188. Results 1 and 2 come from the official registration page and answer the question directly. Result 3 comes from a different source (the Spectator student guide), showing the system can pull complementary perspectives — official process plus student-friendly explanation — for the same question.

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Example Responses

<!-- Provide at least 2 grounded responses (query + response + source attribution)
     and 1 out-of-scope query showing your system's refusal.
     All entries must be text — not screenshots. -->

**Grounded response 1**

Query:

Response:

Source attribution:

---

**Grounded response 2**

Query:

Response:

Source attribution:

---

**Out-of-scope query**

Query:

System response (refusal):

---

## Query Interface

<!-- Describe your query interface: what are the input fields, what does the output look like?
     Then provide a complete sample interaction transcript showing a real exchange. -->

**Input fields:**

**Output format:**

---

**Sample Interaction Transcript**

<!-- Show a complete query → response exchange as it actually appears in your interface.
     Must be text — not a screenshot. -->

> **User:** 

> **System:** 

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
