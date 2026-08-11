# JeevanSetu AI — API Contract

## 1. Purpose

This document defines the communication format between the
WhatsApp/SMS interface, Backend, and AI/RAG service.

All team members should follow this contract during integration.

---

## 2. Main Endpoint

### POST /api/v1/chat

Used to send a user's health query to the JeevanSetu backend.

### Request

```json
{
  "user_id": "demo123",
  "message": "मला डेंग्यूची लक्षणे सांगा",
  "language": "mr",
  "channel": "whatsapp"
}
