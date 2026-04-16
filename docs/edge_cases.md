# Edge Cases for Mutual Fund FAQ Assistant RAG Chatbot

This document catalogs all possible edge cases for comprehensive evaluation of the Mutual Fund FAQ Assistant. Each edge case includes expected behavior, test scenarios, and evaluation criteria.

---

## Table of Contents

1. [Query Input Edge Cases](#1-query-input-edge-cases)
2. [RAG Pipeline Edge Cases](#2-rag-pipeline-edge-cases)
3. [Vector Store Edge Cases](#3-vector-store-edge-cases)
4. [LLM Response Edge Cases](#4-llm-response-edge-cases)
5. [Thread Management Edge Cases](#5-thread-management-edge-cases)
6. [Data Ingestion Edge Cases](#6-data-ingestion-edge-cases)
7. [API/Backend Edge Cases](#7-apibackend-edge-cases)
8. [Frontend/UI Edge Cases](#8-frontendui-edge-cases)
9. [Security Edge Cases](#9-security-edge-cases)
10. [Performance Edge Cases](#10-performance-edge-cases)
11. [Deployment Edge Cases](#11-deployment-edge-cases)

---

## 1. Query Input Edge Cases

### 1.1 Empty/Invalid Input
| Edge Case | Input | Expected Behavior |
|-----------|-------|-------------------|
| EC-Q-001 | Empty string "" | Return 400 error with "Query cannot be empty" message |
| EC-Q-002 | Whitespace only "   " | Return 400 error or trim and reject |
| EC-Q-003 | Null/undefined query | Return 400 error with validation message |
| EC-Q-004 | Query exceeds 500 chars | Return 400 error with "Query too long" message |
| EC-Q-005 | Query exactly at 500 chars | Process successfully |

### 1.2 Special Characters & Encoding
| Edge Case | Input | Expected Behavior |
|-----------|-------|-------------------|
| EC-Q-006 | Unicode characters (Hindi: "म्यूचुअल फंड क्या है") | Process with UTF-8 encoding, return appropriate response |
| EC-Q-007 | Emoji in query "What is NAV? " | Strip or handle emoji, process query |
| EC-Q-008 | HTML tags "<script>alert(1)</script>" | Sanitize input, process as text or reject |
| EC-Q-009 | SQL injection attempt "'; DROP TABLE users; --" | Sanitize, process as literal text |
| EC-Q-010 | JSON injection '{"key": "value"}' | Process as literal text |
| EC-Q-011 | XML/SOAP payload | Process as literal text |
| EC-Q-012 | Control characters \n, \t, \r | Handle gracefully, preserve formatting if meaningful |
| EC-Q-013 | Zero-width characters | Strip or handle appropriately |
| EC-Q-014 | Right-to-left text (Arabic/Hebrew) | Handle UTF-8 bidirectional text |

### 1.3 Query Content Patterns
| Edge Case | Input | Expected Behavior |
|-----------|-------|-------------------|
| EC-Q-015 | Gibberish "asdfghjkl" | Return "I don't understand" or generic mutual fund info |
| EC-Q-016 | Random numbers "123456789" | Treat as literal, may not find relevant context |
| EC-Q-017 | Single character "?" | Return help message or clarification request |
| EC-Q-018 | Only punctuation "?!.,;:" | Return help message |
| EC-Q-019 | Mixed languages "What is म्यूचुअल फंड?" | Process, search for relevant terms |
| EC-Q-020 | Very long word (>100 chars) | Process, may not match any chunks |
| EC-Q-021 | Repeated characters "AAAAAAAAAA" | Process as literal text |
| EC-Q-022 | Palindrome "racecar" | Process normally |
| EC-Q-023 | Mathematical expression "2+2=4" | Process as text, not evaluate |

### 1.4 Query Intent Edge Cases
| Edge Case | Input | Expected Behavior |
|-----------|-------|-------------------|
| EC-Q-024 | Investment advice request "Which fund should I invest in?" | Refuse with advisory disclaimer |
| EC-Q-025 | Future prediction "Will markets go up tomorrow?" | Refuse, state inability to predict |
| EC-Q-026 | Personal finance advice "Should I take loan to invest?" | Refuse with disclaimer |
| EC-Q-027 | Non-mutual fund query "What's the weather today?" | Politely decline, suggest MF topics |
| EC-Q-028 | Offensive/inappropriate content | Filter and return neutral response |
| EC-Q-029 | Competitive comparison "Is HDFC better than SBI?" | Provide factual comparison only |
| EC-Q-030 | Regulatory advice "How to avoid taxes?" | Provide factual tax information only |

### 1.5 PII Detection Edge Cases
| Edge Case | Input | Expected Behavior |
|-----------|-------|-------------------|
| EC-Q-031 | PAN number "ABCDE1234F" | Reject with PII warning |
| EC-Q-032 | Aadhaar number "123456789012" | Reject with PII warning |
| EC-Q-033 | Email address "user@example.com" | Reject with PII warning |
| EC-Q-034 | Phone number "9876543210" | Reject with PII warning |
| EC-Q-035 | Bank account number "12345678901234" | Reject with PII warning |
| EC-Q-036 | Partial PII "My PAN is ABCDE..." | Detect and reject |
| EC-Q-037 | PII with spaces "A B C D E 1 2 3 4 F" | Detect pattern and reject |
| EC-Q-038 | PII in context "My friend ABCDE1234F invested" | Detect and reject |

---

## 2. RAG Pipeline Edge Cases

### 2.1 Retrieval Edge Cases
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-R-001 | No matching chunks in vector store | Return "I don't have information about that" |
| EC-R-002 | Single matching chunk | Use that chunk as context |
| EC-R-003 | All chunks have 0 similarity score | Return fallback response |
| EC-R-004 | All chunks have identical scores | Use top-k (e.g., 5) chunks |
| EC-R-005 | Retrieved chunks exceed context window | Truncate or prioritize |
| EC-R-006 | Retrieved chunks from conflicting sources | Present balanced view or note discrepancy |
| EC-R-007 | Retrieved chunk is empty | Skip and use next chunk |
| EC-R-008 | Retrieved chunk is just whitespace | Skip and use next chunk |
| EC-R-009 | Retrieved chunk contains only metadata | Skip or handle gracefully |
| EC-R-010 | Retrieved chunk is corrupted/invalid | Skip and log error |

### 2.2 Context Assembly Edge Cases
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-R-011 | Context exceeds token limit | Truncate oldest/furthest chunks |
| EC-R-012 | Context exactly at token limit | Process without truncation |
| EC-R-013 | No context available (empty DB) | Return fallback message |
| EC-R-014 | Context from single source | Cite that source |
| EC-R-015 | Context from multiple sources | Cite all relevant sources |
| EC-R-016 | Context contains outdated info | Note date if available |
| EC-R-017 | Context contains duplicate information | Deduplicate or present once |
| EC-R-018 | Context chunks are unordered | Maintain source order or relevance order |

### 2.3 Embedding Generation Edge Cases
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-R-019 | Query embedding generation fails | Return error, log issue |
| EC-R-020 | Document embedding missing | Skip document, log warning |
| EC-R-021 | Embedding dimension mismatch | Return error, check model compatibility |
| EC-R-022 | Embedding contains NaN/Inf values | Handle gracefully, filter or regenerate |
| EC-R-023 | All embeddings are zero vectors | Return error, check model |
| EC-R-024 | Embedding model not available | Return 503 error, suggest retry |

---

## 3. Vector Store Edge Cases

### 3.1 ChromaDB Local Storage
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-V-001 | Vector store directory doesn't exist | Create directory, initialize empty store |
| EC-V-002 | Vector store directory is read-only | Return error with permission message |
| EC-V-003 | Vector store file is corrupted | Log error, attempt recovery or reinitialize |
| EC-V-004 | Disk full during write | Return error, preserve existing data |
| EC-V-005 | Vector store is empty | Return empty results for queries |
| EC-V-006 | Vector store contains 1 document | Process normally |
| EC-V-007 | Vector store contains 10,000+ documents | Process with pagination/limits |
| EC-V-008 | Vector store version mismatch | Migrate or reinitialize |

### 3.2 Chroma Cloud Integration
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-V-009 | Cloud credentials missing | Fall back to local storage or error |
| EC-V-010 | Cloud credentials invalid | Return auth error, suggest check |
| EC-V-011 | Cloud service unavailable | Retry with backoff, fallback to local |
| EC-V-012 | Cloud rate limit exceeded | Retry after delay, queue requests |
| EC-V-013 | Cloud quota exceeded | Log warning, use local storage |
| EC-V-014 | Network timeout to cloud | Retry, then fallback to local |
| EC-V-015 | Cloud collection doesn't exist | Create collection or error |
| EC-V-016 | Cloud collection name conflict | Use unique name or error |

### 3.3 Vector Operations
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-V-017 | Adding duplicate document | Update existing or skip (idempotent) |
| EC-V-018 | Deleting non-existent document | Return success (idempotent) or warning |
| EC-V-019 | Updating non-existent document | Create new or return error |
| EC-V-020 | Batch add with partial failures | Rollback or continue with logging |
| EC-V-021 | Search with invalid filter syntax | Return error with valid syntax hint |
| EC-V-022 | Search with no filters | Return all results (limited) |
| EC-V-023 | Search with too restrictive filters | Return empty results |

---

## 4. LLM Response Edge Cases

### 4.1 Groq API Edge Cases
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-L-001 | Groq API key missing | Return 500 error with config message |
| EC-L-002 | Groq API key invalid | Return 401 error, suggest check |
| EC-L-003 | Groq rate limit exceeded | Retry with exponential backoff |
| EC-L-004 | Groq service unavailable | Return 503, suggest retry later |
| EC-L-005 | Groq request timeout | Retry or return timeout message |
| EC-L-006 | Groq returns empty response | Return fallback message |
| EC-L-007 | Groq returns malformed JSON | Handle gracefully, extract text if possible |
| EC-L-008 | Groq model deprecated | Update model or return error |
| EC-L-009 | Context window exceeded | Truncate and retry |
| EC-L-010 | Max tokens too low for response | Increase or return truncated response |

### 4.2 Response Content Edge Cases
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-L-011 | Response exceeds 3 sentences | Truncate or regenerate |
| EC-L-012 | Response contains hallucinations | Compare with context, flag if divergent |
| EC-L-013 | Response contradicts context | Regenerate or flag issue |
| EC-L-014 | Response contains PII | Filter and sanitize |
| EC-L-015 | Response contains offensive content | Filter and regenerate |
| EC-L-016 | Response is empty string | Return fallback message |
| EC-L-017 | Response is only whitespace | Return fallback message |
| EC-L-018 | Response contains code/markup | Strip or escape |
| EC-L-019 | Response language doesn't match query | Request regeneration |
| EC-L-020 | Response contains investment advice | Regenerate with stronger refusal |

### 4.3 Response Format Edge Cases
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-L-021 | Response missing required fields | Return error or populate defaults |
| EC-L-022 | Response has extra fields | Accept and ignore extras |
| EC-L-023 | Source URL missing in response | Use most relevant chunk source |
| EC-L-024 | Last updated date missing | Use current date or omit |
| EC-L-025 | Thread ID missing | Generate new or use request ID |
| EC-L-026 | Query type classification fails | Default to "unknown" |
| EC-L-027 | Disclaimer missing | Add default disclaimer |

---

## 5. Thread Management Edge Cases

### 5.1 Thread Creation
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-T-001 | Create thread with no messages | Create empty thread |
| EC-T-002 | Create thread with initial message | Create thread with that message |
| EC-T-003 | Thread ID generation collision | Retry with new UUID |
| EC-T-004 | Database locked during creation | Retry with backoff |
| EC-T-005 | Thread limit reached | Archive old or reject new |

### 5.2 Thread Retrieval
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-T-006 | Request non-existent thread | Return 404 error |
| EC-T-007 | Request thread with invalid ID format | Return 400 error |
| EC-T-008 | Request thread with empty ID | Return 400 error |
| EC-T-009 | Request deleted thread | Return 404 or 410 (gone) |
| EC-T-010 | Database corruption for thread | Return 500, log error |

### 5.3 Thread Context Window
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-T-011 | Thread has 0 messages | Start fresh conversation |
| EC-T-012 | Thread has 1 message | Include in context |
| EC-T-013 | Thread has exactly 5 messages | Include all in context |
| EC-T-014 | Thread has 6+ messages | Include last 5 only |
| EC-T-015 | Thread has 100+ messages | Include last 5, log warning |
| EC-T-016 | Thread messages exceed token limit | Truncate oldest messages |
| EC-T-017 | Thread has very long messages | Truncate individual messages |
| EC-T-018 | Thread has corrupted message | Skip that message, log error |

### 5.4 Thread Isolation
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-T-019 | Concurrent queries on same thread | Queue or reject second request |
| EC-T-020 | Concurrent queries on different threads | Process independently |
| EC-T-021 | Query with wrong thread ID | Return 404 or create new thread |
| EC-T-022 | Thread data leaks to another thread | Security violation, investigate |
| EC-T-023 | Thread context mixed with another | Security violation, investigate |

### 5.5 Thread Deletion
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-T-024 | Delete non-existent thread | Return 404 or success (idempotent) |
| EC-T-025 | Delete thread with active query | Wait or cancel query |
| EC-T-026 | Delete already deleted thread | Return 404 or success |
| EC-T-027 | Bulk delete threads | Delete all or none (atomic) |

---

## 6. Data Ingestion Edge Cases

### 6.1 Scraping Edge Cases
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-I-001 | URL returns 404 | Log error, skip URL, continue |
| EC-I-002 | URL returns 500 | Retry, then skip if persistent |
| EC-I-003 | URL returns 403 (forbidden) | Log error, skip URL |
| EC-I-004 | URL timeout | Retry with longer timeout, then skip |
| EC-I-005 | SSL certificate error | Log warning, skip or retry with verify=False |
| EC-I-006 | Redirect loop | Detect and skip |
| EC-I-007 | Infinite page (streaming) | Timeout and skip |
| EC-I-008 | Page requires JavaScript | Log warning, skip or use headless |
| EC-I-009 | Page requires authentication | Log error, skip |
| EC-I-010 | Rate limited (429) | Backoff and retry |
| EC-I-011 | DNS resolution fails | Log error, skip |
| EC-I-012 | Connection refused | Log error, skip |
| EC-I-013 | Empty page content | Log warning, skip |
| EC-I-014 | Binary content (non-text) | Log warning, skip |
| EC-I-015 | Very large page (>10MB) | Stream or skip |
| EC-I-016 | Malformed HTML | Parse with lenient parser |
| EC-I-017 | Encoding detection fails | Try UTF-8 fallback |

### 6.2 PDF Processing Edge Cases
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-I-018 | PDF is corrupted | Log error, skip |
| EC-I-019 | PDF is password protected | Log error, skip |
| EC-I-020 | PDF is scanned image (no text) | OCR or skip |
| EC-I-021 | PDF has 0 pages | Log warning, skip |
| EC-I-022 | PDF has 1000+ pages | Process first N pages or batch |
| EC-I-023 | PDF text extraction fails | Log error, skip |
| EC-I-024 | PDF contains only images | Log warning, skip |
| EC-I-025 | PDF font encoding issues | Use fallback encoding |

### 6.3 Chunking Edge Cases
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-I-026 | Document has 0 characters | Log warning, skip |
| EC-I-027 | Document has 1 character | Create single chunk |
| EC-I-028 | Document has exactly chunk size | Create single chunk |
| EC-I-029 | Document exceeds max chunk size | Split into multiple chunks |
| EC-I-030 | Document has no sentence boundaries | Split by character count |
| EC-I-031 | Document has only headers | Create metadata chunks |
| EC-I-032 | Document has tables | Preserve table structure |
| EC-I-033 | Document has code blocks | Preserve formatting |
| EC-I-034 | Document has mixed languages | Handle UTF-8 |
| EC-I-035 | Chunk overlap calculation error | Use default overlap |

### 6.4 Embedding Generation Edge Cases
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-I-036 | Empty chunk text | Skip chunk, log warning |
| EC-I-037 | Chunk text is whitespace only | Skip chunk |
| EC-I-038 | Chunk exceeds model max length | Truncate or split |
| EC-I-039 | Embedding model download fails | Use cached or error |
| EC-I-040 | GPU out of memory | Fall back to CPU |
| EC-I-041 | Batch embedding partial failure | Retry individually |
| EC-I-042 | All chunks fail embedding | Log error, skip document |

### 6.5 Vector Store Update Edge Cases
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-I-043 | Duplicate document ID | Update existing |
| EC-I-044 | Metadata serialization fails | Skip metadata or use string |
| EC-I-045 | Vector store write fails | Retry, then log error |
| EC-I-046 | Partial batch write | Rollback or retry |
| EC-I-047 | Collection recreation needed | Backup and recreate |

---

## 7. API/Backend Edge Cases

### 7.1 Request Handling
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-A-001 | Request body too large (>1MB) | Return 413 error |
| EC-A-002 | Request with invalid JSON | Return 400 with parse error |
| EC-A-003 | Request with missing Content-Type | Assume JSON or return 400 |
| EC-A-004 | Request with wrong Content-Type | Return 415 error |
| EC-A-005 | Request with malformed headers | Return 400 or ignore |
| EC-A-006 | Request with unknown query params | Ignore or return 400 |

### 7.2 Authentication/Authorization
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-A-007 | Missing API key | Return 401 if required |
| EC-A-008 | Invalid API key format | Return 401 |
| EC-A-009 | Expired API key | Return 401 |
| EC-A-010 | Revoked API key | Return 401 |
| EC-A-011 | Rate limit per API key exceeded | Return 429 with retry-after |

### 7.3 Response Handling
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-A-012 | Response serialization fails | Return 500, log error |
| EC-A-013 | Response exceeds max size | Truncate or stream |
| EC-A-014 | Client disconnects mid-request | Cancel processing, log |
| EC-A-015 | Response compression fails | Send uncompressed |

### 7.4 Health & Status
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-A-016 | Database connection lost | Return unhealthy status |
| EC-A-017 | Vector store unavailable | Return degraded status |
| EC-A-018 | LLM service unavailable | Return degraded status |
| EC-A-019 | All services down | Return unhealthy status |
| EC-A-020 | Health check timeout | Return timeout status |

---

## 8. Frontend/UI Edge Cases

### 8.1 Input Handling
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-F-001 | User types 500+ characters | Show character counter, disable submit |
| EC-F-002 | User pastes formatted text | Strip formatting |
| EC-F-003 | User pastes image | Show "text only" message |
| EC-F-004 | User submits with Enter key | Submit query |
| EC-F-005 | User submits empty query | Disable submit button |
| EC-F-006 | User types very fast | Debounce input |
| EC-F-007 | User uses browser autofill | Accept if text |

### 8.2 Thread Sidebar
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-F-008 | 0 threads exist | Show "No conversations" message |
| EC-F-009 | 100+ threads exist | Implement pagination or scroll |
| EC-F-010 | Thread title is very long | Truncate with ellipsis |
| EC-F-011 | Thread has no messages | Show "New conversation" |
| EC-F-012 | Thread deletion confirmation | Show modal, require confirm |
| EC-F-013 | Mobile view thread list | Show hamburger menu |
| EC-F-014 | Thread list fails to load | Show error, retry button |

### 8.3 Chat Display
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-F-015 | Message is very long | Implement scroll |
| EC-F-016 | Message contains URLs | Auto-link URLs |
| EC-F-017 | Message contains markdown | Render or escape |
| EC-F-018 | Message contains code | Syntax highlight |
| EC-F-019 | Message has special chars | Escape HTML |
| EC-F-020 | Source URL is broken | Show as text, not link |
| EC-F-021 | Response streaming | Show typing indicator |
| EC-F-022 | Response timeout | Show timeout message |

### 8.4 Network/Error Handling
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-F-023 | Network disconnected | Show offline indicator |
| EC-F-024 | API returns 500 | Show error message |
| EC-F-025 | API returns 429 | Show rate limit message |
| EC-F-026 | Request timeout | Show retry option |
| EC-F-027 | CORS error | Show config error |
| EC-F-028 | Browser storage full | Clear old threads |
| EC-F-029 | Session expired | Redirect to start |

### 8.5 Browser Compatibility
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-F-030 | Internet Explorer | Show unsupported message |
| EC-F-031 | JavaScript disabled | Show noscript message |
| EC-F-032 | Cookies disabled | Warn about thread persistence |
| EC-F-033 | LocalStorage disabled | Warn about persistence |
| EC-F-034 | Very small viewport | Mobile responsive layout |
| EC-F-035 | Very large viewport | Max-width container |
| EC-F-036 | High DPI display | Scale UI appropriately |
| EC-F-037 | Reduced motion preference | Disable animations |
| EC-F-038 | Dark mode preference | Support dark theme |

---

## 9. Security Edge Cases

### 9.1 Input Validation
| Edge Case | Attack Vector | Expected Behavior |
|-----------|---------------|-------------------|
| EC-S-001 | XSS in query | Sanitize, escape output |
| EC-S-002 | XSS in response | Sanitize LLM output |
| EC-S-003 | CSRF attempt | Validate origin/token |
| EC-S-004 | Path traversal | Validate file paths |
| EC-S-005 | Command injection | Never execute user input |
| EC-S-006 | Template injection | Use safe templating |
| EC-S-007 | LDAP injection | Not applicable (no LDAP) |
| EC-S-008 | XML External Entity | Disable XML parsing |

### 9.2 Data Protection
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-S-009 | PII in logs | Mask PII before logging |
| EC-S-010 | PII in error messages | Sanitize error output |
| EC-S-011 | Thread data in URL | Use POST, not GET |
| EC-S-012 | Sensitive data in localStorage | Encrypt or avoid |
| EC-S-013 | API key in frontend | Never expose keys |
| EC-S-014 | Credentials in git | Use .env, .gitignore |

### 9.3 Access Control
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-S-015 | Access another user's thread | Return 403 |
| EC-S-016 | Modify another user's thread | Return 403 |
| EC-S-017 | Delete another user's thread | Return 403 |
| EC-S-018 | Enumerate thread IDs | Rate limit, return 404 |
| EC-S-019 | Brute force thread ID | Rate limit |

---

## 10. Performance Edge Cases

### 10.1 Load Handling
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-P-001 | Single user, 100 rapid queries | Queue or rate limit |
| EC-P-002 | 100 concurrent users | Scale horizontally |
| EC-P-003 | Spike traffic (10x normal) | Auto-scale or queue |
| EC-P-004 | Sustained high load | Degrade gracefully |
| EC-P-005 | DDOS attack | Rate limit, block IPs |

### 10.2 Resource Limits
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-P-006 | Memory exhaustion | OOM killer, restart |
| EC-P-007 | CPU at 100% | Queue requests |
| EC-P-008 | Disk full | Log error, alert |
| EC-P-009 | File descriptor limit | Close idle connections |
| EC-P-010 | Network bandwidth limit | Compress responses |

### 10.3 Timing
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-P-011 | Query takes >30s | Timeout, return error |
| EC-P-012 | Embedding takes >10s | Timeout, retry |
| EC-P-013 | LLM response takes >20s | Timeout, retry |
| EC-P-014 | Vector search takes >5s | Optimize or cache |
| EC-P-015 | Cold start delay | Pre-warm instances |

---

## 11. Deployment Edge Cases

### 11.1 Render Deployment
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-D-001 | Build fails | Log error, don't deploy |
| EC-D-002 | Start command fails | Rollback, alert |
| EC-D-003 | Health check fails | Don't route traffic |
| EC-D-004 | Instance crashes | Auto-restart |
| EC-D-005 | Instance memory limit | Optimize or upgrade |
| EC-D-006 | Instance CPU limit | Optimize or upgrade |
| EC-D-007 | Disk ephemeral, data lost | Use external storage |
| EC-D-008 | Environment variables missing | Fail fast, log error |

### 11.2 Vercel Deployment
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-D-009 | Build timeout | Optimize build |
| EC-D-010 | Function size limit | Split functions |
| EC-D-011 | Edge function error | Fallback to serverless |
| EC-D-012 | Static generation fails | Use SSR fallback |
| EC-D-013 | API route timeout | Optimize or split |

### 11.3 Chroma Cloud
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-D-014 | Cloud migration | Backup, migrate, verify |
| EC-D-015 | Cloud outage | Fallback to local |
| EC-D-016 | Cloud data corruption | Restore from backup |
| EC-D-017 | Cloud quota exceeded | Alert, upgrade plan |

### 11.4 GitHub Actions
| Edge Case | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| EC-D-018 | Scheduler fails | Alert, manual trigger |
| EC-D-019 | Scheduler partial success | Continue with available data |
| EC-D-020 | Secrets expired | Fail, alert |
| EC-D-021 | Workflow disabled | Alert, re-enable |
| EC-D-022 | Runner out of disk | Clean up, retry |

---

## Evaluation Checklist

Use this checklist to evaluate the system against edge cases:

### Query Input (EC-Q-001 to EC-Q-038)
- [ ] Empty/invalid inputs handled
- [ ] Special characters handled
- [ ] PII detection working
- [ ] Query length limits enforced
- [ ] Encoding issues handled

### RAG Pipeline (EC-R-001 to EC-R-024)
- [ ] Empty retrieval handled
- [ ] Context assembly working
- [ ] Token limits respected
- [ ] Embedding generation stable
- [ ] Similarity scoring accurate

### Vector Store (EC-V-001 to EC-V-023)
- [ ] Local storage resilient
- [ ] Cloud fallback working
- [ ] CRUD operations stable
- [ ] Search filters working
- [ ] Error recovery implemented

### LLM Response (EC-L-001 to EC-L-027)
- [ ] API errors handled
- [ ] Response validation working
- [ ] Content filtering active
- [ ] Format compliance checked
- [ ] Fallback messages ready

### Thread Management (EC-T-001 to EC-T-027)
- [ ] Thread isolation verified
- [ ] Context window managed
- [ ] Concurrent access safe
- [ ] CRUD operations stable
- [ ] Data persistence reliable

### Data Ingestion (EC-I-001 to EC-I-047)
- [ ] Scraping errors handled
- [ ] PDF processing robust
- [ ] Chunking stable
- [ ] Embedding batch processing
- [ ] Vector store updates atomic

### API/Backend (EC-A-001 to EC-A-020)
- [ ] Request validation strict
- [ ] Error responses informative
- [ ] Health checks accurate
- [ ] Rate limiting active
- [ ] Timeout handling proper

### Frontend/UI (EC-F-001 to EC-F-038)
- [ ] Input validation client-side
- [ ] Error messages user-friendly
- [ ] Responsive design working
- [ ] Accessibility supported
- [ ] Browser compatibility verified

### Security (EC-S-001 to EC-S-019)
- [ ] XSS prevention active
- [ ] CSRF protection enabled
- [ ] PII handling compliant
- [ ] Access control enforced
- [ ] Audit logging complete

### Performance (EC-P-001 to EC-P-015)
- [ ] Load testing passed
- [ ] Resource limits monitored
- [ ] Timeout handling working
- [ ] Caching effective
- [ ] Scaling triggers configured

### Deployment (EC-D-001 to EC-D-022)
- [ ] Health checks passing
- [ ] Rollback procedure tested
- [ ] Monitoring alerts active
- [ ] Backup/recovery verified
- [ ] CI/CD pipeline stable

---

## Test Execution Guide

### Priority Levels
- **P0 (Critical)**: Must pass before production
- **P1 (High)**: Should pass, workarounds acceptable
- **P2 (Medium)**: Nice to have, document limitations
- **P3 (Low)**: Future improvements

### Priority Assignment

**P0 Edge Cases:**
- EC-Q-001, EC-Q-004, EC-Q-031-038 (Input validation, PII)
- EC-R-001, EC-R-013 (Empty retrieval)
- EC-L-001, EC-L-020 (LLM errors, advice refusal)
- EC-T-019-023 (Thread isolation)
- EC-S-001-019 (Security)

**P1 Edge Cases:**
- EC-Q-006-010 (Special characters)
- EC-R-002-012 (Retrieval variations)
- EC-V-001-008 (Vector store local)
- EC-A-001-005 (API validation)
- EC-F-001-007 (Frontend input)

**P2 Edge Cases:**
- EC-Q-011-030 (Content patterns)
- EC-I-001-047 (Ingestion variations)
- EC-P-001-015 (Performance)
- EC-D-001-022 (Deployment)

**P3 Edge Cases:**
- EC-F-030-038 (Browser compatibility)
- EC-Q-021-023 (Unusual patterns)

---

## Notes

- This document should be updated as new edge cases are discovered
- Each edge case should have a corresponding test case
- Failed edge cases should be tracked as bugs
- Edge case coverage should be reviewed quarterly
