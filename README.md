# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

Columbia University student life — specifically CS academic requirements, housing lottery strategy, dining options near campus, and disability accommodations. This knowledge is valuable because the most useful advice is scattered across dozens of university websites, student blogs, and campus publications rather than in one searchable place. Official sources explain policy but not strategy — a student asking "how do I actually get a good room in the housing lottery?" needs Bwog, not the housing office website.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Columbia CS FAQ | Official university page | https://www.cs.columbia.edu/undergrad-faq/ |
| 2 | CS Program Overview | Official university page | https://www.cs.columbia.edu/education/undergraduate/ |
| 3 | Housing Lottery Points | Official university page | https://www.housing.columbia.edu/content/point-values-lottery-numbers-selection-appointments |
| 4 | Room Selection Guide | Official university page | https://www.housing.columbia.edu/roomselection |
| 5 | Bwog Housing Strategy | Student blog post | https://bwog.com/2026/02/columbia-housing-strategy-for-rising-sophomores/ |
| 6 | ODS Registration | Official university page | https://www.health.columbia.edu/services/register-disability-services |
| 7 | Spectator ODS Guide | Student newspaper article | https://www.columbiaspectator.com/spectrum/2022/12/04/a-guide-to-navigating-accommodations-with-disability-services/ |
| 8 | Morningside Heights Eating | Student newspaper article | https://www.columbiaspectator.com/arts-and-culture/2022/08/26/a-beginners-guide-to-morningside-heights-eating/ |
| 9 | Dining Halls Guide | Student blog post | https://tcadmission.com/2024/09/24/your-guide-to-the-best-dining-halls-at-columbia/ |
| 10 | SEAS Advising Guide | Official university page | https://www.cc-seas.columbia.edu/csa/advising_seas |
---

## Chunking Strategy

**Chunk size:** 500 characters per chunk.

**Overlap:** 100 characters. The chunker carries the last sentence or two from each chunk into the start of the next, so facts near a boundary are retrievable from at least one chunk.

**Why these choices fit your documents:** My sources are a mix of long FAQ guides and medium-length articles, not short reviews. A 500-character chunk typically captures one complete Q&A pair or one to two paragraphs — enough semantic content for the embedding model to produce a meaningful vector. Too small (under 200 characters) would strip context from multi-sentence policy explanations. Too large (over 1000 characters) would merge unrelated topics into one chunk, diluting retrieval precision. I also switched from raw character-count splitting to sentence-aware splitting after discovering my first implementation cut chunks mid-word. The final chunker groups whole sentences until adding the next would exceed 500 characters, then closes the chunk cleanly on a sentence boundary.

**Preprocessing:** HTML tags stripped using BeautifulSoup. Navigation menus, footers, cookie banners, author bios, and social media prompts removed. For JavaScript-rendered pages that BeautifulSoup could not parse, article text was manually extracted from embedded JSON blobs and cleaned using Find and Replace in VS Code.

**Final chunk count:** 134 chunks across 10 documents.

---

## Sample Chunks

| # | Source document | Chunk text |
|---|----------------|------------|
| 1 | cs_faq.txt | FAQ for Currently Enrolled Undergraduates \| Department of Computer Science, Columbia University. Have a question or concern about your program? You're in the right place! GENERAL ADVISING & MAJOR DECLARATION When can I declare CS as my major? |
| 2 | cs_faq.txt | When can I declare CS as my major? Are there any minimum requirements that I need to meet before declaring the major? The major declaration period occurs during your sophomore year: in the fall semester for SEAS students and the spring semester for Columbia College, GS, and Barnard students. |
| 3 | bwog_housing_strategy.txt | The only way to bring up your lottery number is to have rising junior(s) in your group, as they have a higher point value. Lottery numbers are otherwise randomly generated within your lottery number range. All beds in an apartment or double must be filled in order to select into a space. |
| 4 | ods_registration.txt | Disability Services reviews each request and determines eligibility for accommodations and services. The review process does not begin until your completed registration form and your disability documentation are received. The review process takes approximately three weeks. |
| 5 | dining_halls_guide.txt | John Jay - Biggest, decent selection, has meatless mondays (which is tragic imo). JJ's Diner - Smallest, is basically just junk food, is open very late. Ferris Booth Commons - Generally has the nicest food, always decently busy. |

**Total chunk count: 134 chunks across 10 documents.**

This falls comfortably within the healthy range (more than 50, less than 2,000), indicating chunk size is reasonable — not so large that topics get diluted, not so small that individual chunks lose meaning.

Each chunk above is a complete, self-contained thought ending on a real sentence boundary. My first implementation used raw character-count slicing, which cut chunks mid-word (e.g., "Are ther" instead of "Are there"). I rewrote `chunk_text()` to group whole sentences instead, fixing this issue.

## Embedding Model


**Model used:** all-MiniLM-L6-v2 via sentence-transformers, running locally with no API key required. It produces 384-dimensional embeddings and is optimized for semantic similarity tasks.

**Production tradeoff reflection:** For a real deployment I would evaluate text-embedding-3-large from OpenAI, which produces higher-quality embeddings on domain-specific text and supports longer context windows — useful for larger document chunks. The tradeoff is cost (API pricing per token vs. free local inference), latency (network round-trip vs. local CPU), and data privacy (student content sent to an external API vs. staying on-device). For a Columbia student tool handling potentially sensitive academic and disability-related content, the local model's privacy advantage is significant. I would also consider a multilingual model if expanding to international student communities.

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

**System prompt grounding instruction:**
"You are a helpful assistant for Columbia University students. Answer questions using ONLY the information provided in the context below. Do not use any outside knowledge, even if you are confident about it. If the provided context does not contain enough information to answer the question, respond with exactly: 'I don't have enough information on that in my documents.' Always cite which source document(s) your answer came from."

**How source attribution is surfaced in the response:**
Source attribution works in two ways. First, the user message formats each retrieved chunk as "[Document N - source: filename]" so the LLM can cite specific documents inline. Second, after generation, the code programmatically collects all unique source filenames from the retrieved chunks and appends them to the response as a Sources list — this ensures attribution appears even if the LLM forgets to cite inline.

---

## Example Responses

**Grounded response 1**

Query: How does the Columbia housing lottery actually work?

Response: The Columbia housing lottery works by assigning a lottery number to each group or individual, with groups receiving one lottery number (Document 1 - source: bwog_housing_strategy, Document 4 - source: housing_lottery_points). The lottery numbers determine the order of Room Selection appointments, with students having higher class standing receiving a higher point value, a lower lottery number, and an earlier Room Selection appointment time (Document 3 - source: housing_lottery_points). Individuals or groups with lottery numbers closer to 1 will have appointment times towards the beginning of Room Selection, while those with numbers closer to 5000 will have appointment times towards the end. If a room is not selected during Room Selection, students will be put on the Guaranteed Assignment List and given a housing assignment by late July.

Source attribution: bwog_housing_strategy, housing_lottery_points

---

**Grounded response 2**

Query: How do I register for disability accommodations at Columbia?

Response: To register for disability accommodations at Columbia, you can start by filling out the registration form or attending DS Drop-in Hours (Document 2 - source: ods_registration). You may submit the required materials via email, fax (212-854-3448), or drop them off in person at Wien Hall Suite 108A (Document 1 - source: ods_registration). A step-by-step breakdown is also available on the Columbia Health website (Document 3 - source: spectator_ods_guide).

Source attribution: ods_registration, spectator_ods_guide

---

**Out-of-scope query**

Query: What GPA do I need to get into Harvard Law School?

System response (refusal): I don't have enough information on that in my documents.

---

## Query Interface

**Input fields:** A single text box labeled "Your question" with placeholder text "e.g. How does the housing lottery work?"

**Output format:** Two text boxes side by side — "Answer" (10 lines) showing the grounded LLM response with inline source citations, and "Retrieved from" (4 lines) showing a bullet list of source document filenames.

---

**Sample Interaction Transcript**

User input: How does the Columbia housing lottery actually work?

Answer: The Columbia housing lottery works by assigning a lottery number to each group or individual, with groups receiving one lottery number. The lottery numbers determine the order of Room Selection appointments, with students having higher class standing receiving a higher point value, a lower lottery number, and an earlier Room Selection appointment time. Individuals or groups with lottery numbers closer to 1 will have appointment times towards the beginning of Room Selection, while those with numbers closer to 5000 will have appointment times towards the end. If a room is not selected during Room Selection, students will be put on the Guaranteed Assignment List and given a housing assignment by late July, with Housing trying to keep groups together and considering building preferences. (Sources: bwog_housing_strategy, housing_lottery_points)

Retrieved from:
- bwog_housing_strategy
- housing_lottery_points

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | How does the Columbia housing lottery actually work? | Lottery numbers assigned by seniority points; seniors get lowest numbers and earliest appointments | Correctly explained point values, lottery number ranges by class year, appointment order, and Guaranteed Assignment List | Relevant | Accurate |
| 2 | What is the best dining hall at Columbia? | Ferris Booth Commons generally considered best food quality | Retrieved dining hall descriptions and event listings but did not directly compare or rank dining halls by quality | Partially relevant | Partially accurate |
| 3 | How do I register for disability accommodations at Columbia? | Submit registration form to ODS, takes 3 weeks to review, then meet with coordinator | Correctly described registration form, submission methods including Wien Hall drop-off, and linked to Columbia Health website, citing two sources | Relevant | Accurate |
| 4 | What CS courses should I take first as a Columbia CS major? | ENGI E1006 and COMS W1004 recommended in freshman year | "I don't have enough information on that in my documents." — despite the answer being present in cs_faq.txt | Off-target | Inaccurate |
| 5 | What do students recommend for cheap food near Columbia? | Fumo $12 pasta, halal cart, Absolute Bagels | Found Fumo's $12 pasta special and mentioned other nearby restaurants but missed the halal cart and most price-specific recommendations | Partially relevant | Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** What CS courses should I take first as a Columbia CS major?

**What the system returned:** "I don't have enough information on that in my documents." — a refusal to answer, despite the answer being present in cs_faq.txt: "we do recommend that you start taking the introductory CS courses (ENGI E1006, COMS W1004) during your freshman year."

**Root cause (tied to a specific pipeline stage):** This is a retrieval failure caused by vocabulary mismatch. The query phrase "what courses should I take first" did not semantically match the FAQ's phrasing "we recommend that you start taking the introductory CS courses." The embedding model mapped these two phrasings to different regions of the vector space, so the relevant chunk never ranked in the top 5 retrieved results. The LLM then correctly declined to answer — the generation step worked as intended — but it had nothing useful to work with because retrieval failed upstream.

**What you would change to fix it:** Increase top-k from 5 to 8 to cast a wider retrieval net, which would improve the chances of surfacing this chunk even with imperfect semantic matching. A more robust fix would be query rewriting — paraphrasing the user's question into several alternative phrasings before embedding, then taking the union of top results. For example, rewriting "what courses should I take first" as "recommended introductory CS courses for freshmen" before embedding would likely retrieve the correct chunk.


## Spec Reflection

**One way the spec helped you during implementation:**
The planning.md chunking strategy section forced me to think through chunk size before writing any code. Specifying 500 characters with 100 overlap upfront meant that when my first implementation produced mid-word cuts, I had a clear target to debug toward — I knew the numbers were right but the splitting method was wrong, which led me directly to the sentence-aware fix rather than randomly adjusting parameters.

**One way your implementation diverged from the spec, and why:**
My spec assumed I would scrape all 10 sources automatically via requests and BeautifulSoup. In practice, 3 sources (housing.columbia.edu and health.columbia.edu) returned 403 errors blocking automated scraping, and 2 Spectator articles used JavaScript rendering that BeautifulSoup could not parse. I ended up manually extracting content from these 5 sources — a hybrid approach the spec did not anticipate. I updated ingest.py to check for existing clean files first, so manually-saved documents are used when scraping fails.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* My Chunking Strategy section from planning.md, asking Claude to implement chunk_text() with 500-character chunks and 100-character overlap.
- *What it produced:* A sliding window character-count chunker that split text every 500 characters regardless of sentence boundaries, producing fragments like "Are ther" mid-word.
- *What I changed or overrode:* I identified the mid-word cutting problem by inspecting sample chunks, then directed Claude to rewrite the function to respect sentence boundaries. When the new version caused an infinite loop on long sentences, I diagnosed the cause (a single sentence longer than chunk_size with no escape path) and asked Claude to add a safety valve for that edge case.

**Instance 2**

- *What I gave the AI:* The raw HTML of JavaScript-rendered Columbia Spectator articles, asking Claude to extract only the article body text.
- *What it produced:* It identified the Fusion.globalContent JSON blob embedded in the page script tag and showed me the paragraph text structure inside it.
- *What I changed or overrode:* Claude identified the pattern but I did all the actual file editing myself — using Find and Replace in VS Code to remove JSON separators and HTML tags, manually verifying each paragraph was clean before saving. I also decided to skip the author bio and social media paragraphs at the end, which Claude had included in its extraction.