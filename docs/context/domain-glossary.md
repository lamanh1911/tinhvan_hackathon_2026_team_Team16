# Domain Glossary

| Term | Definition |
|---|---|
| AI Sales Follow-up Assistant | The system — automates post-networking and post-meeting communication workflows. |
| Networking event | Business networking event where Sales meets and exchanges business cards with prospects. |
| Business meeting | A meeting with a customer, either online or offline. |
| Follow-up | Contacting a customer again after a first meeting or after a formal meeting, usually by email. |
| Thank-you email | Appreciation email sent after exchanging business cards, customized with the event name and meeting date. |
| Follow-up email | Email sent after a meeting summarizing discussion points, next actions, and relevant attachments. |
| Draft | AI-generated content (email, MOM) awaiting human review before use or sending. |
| Human-in-the-loop | Core principle: AI creates drafts or proposals; humans review and make the final decision. |
| OCR | Optical Character Recognition — reads text from a business card image. |
| Card scanner module | Internal module combining OCR and AI extraction to digitize business card information. No third-party apps. |
| Confidence | A score assigned to each extracted field indicating how certain the extraction is. Low-confidence fields are flagged. |
| MOM | Minutes of Meeting — structured summary containing: main points, next actions, owners, deadlines. |
| Transcript | Text record of a Teams meeting, used as input for MOM generation. |
| Recording | Audio or video recording of a Teams meeting, alternative source when transcript is unavailable. |
| Next action | A specific task agreed upon during a meeting, with an assigned owner and deadline. |
| Action item | Equivalent to next action — an individual task entry within MOM. |
| Slot | A proposed time window for a meeting. |
| Calendar | A team member's schedule, read from Teams Calendar via Microsoft Graph. |
| Free/busy | A member's availability at a given time slot. |
| Company visit | A special calendar note — offline meeting slots must not conflict with events marked "Company visit". |
| Travel buffer | Extra time added around an offline meeting slot to account for travel between locations. |
| Template | Fixed company email template used for brand consistency. |
| PII | Personally Identifiable Information — customer name, email, and phone. Must not appear in logs. |
| Microsoft Graph | Unified Microsoft API for accessing Outlook, Teams Calendar, and Transcript. |
| OpenRouter | LLM gateway used to access language models for email generation, MOM summarization, and field extraction. |
| LLM | Large Language Model — used for generating drafts and summarizing content. |
| BrSE | Bridge System Engineer — liaison between customer and development team. Can review and approve MOM. |
| Sales | Primary user role — owns customer relationships, triggers workflows, sends emails. |
| Admin | System administrator — manages configuration, templates, and permissions. |
| Presales | Pre-sales support team member who may need to attend certain meetings. |
| Draft status | Lifecycle of a draft: `draft` → `in_review` → `approved` → `sent` (or `rejected`). |
