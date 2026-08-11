# JeevanSetu  — API Contract

## 1. Purpose

This document defines how the WhatsApp/SMS interface, Backend,
AI/RAG and Healthcare Data modules communicate with each other.

All team members should follow this contract during integration.

---

## 2. Main Chat Endpoint

### POST /api/v1/chat

Used to send a user's health query to the backend.

### Request

```json
{
  "user_id": "demo123",
  "message": "मला डेंग्यूची लक्षणे सांगा",
  "language": "mr",
  "channel": "whatsapp"
}
