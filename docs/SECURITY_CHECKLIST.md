# JeevanSetu Security Checklist

## Backend
- [ ] API input validation
- [ ] Oversized request handling
- [ ] Invalid JSON handling
- [ ] Error/stack-trace leakage
- [ ] CORS configuration
- [ ] Rate limiting
- [ ] Unauthorized API access
- [ ] API key protection
- [ ] MongoDB credential protection

## AI / RAG
- [ ] Prompt injection
- [ ] System prompt extraction
- [ ] Medical misinformation
- [ ] Unsafe diagnosis/prescription requests
- [ ] Vaccination misinformation
- [ ] Sensitive information leakage
- [ ] Hallucination/fallback testing

## WhatsApp / SMS
- [ ] Webhook validation
- [ ] Unauthorized webhook requests
- [ ] Replay/duplicate requests
- [ ] Malicious message handling
- [ ] API credential protection

## Integration
- [ ] M1 → M2
- [ ] M2 → M3
- [ ] M1 → M4
- [ ] MongoDB
- [ ] End-to-end request/response