---
name: mail
description: "Composing mail through Apple Mail via macuse. Use when drafting, replying to, or forwarding email. Covers the double-encoding bug that garbles accented characters and the attachment workaround. Triggers on 'draft an email', 'reply to this', 'forward that', 'stuur een mail', 'mail hem', 'send this to'."
---

# Mail

Whatever lands in a Mail draft must be clean. No mojibake, no stray characters. A garbled accent in a draft Mischa opens is unacceptable.

The macuse Apple Mail tools (`mail_reply_message`, `mail_compose_message`, `mail_forward_message`) double-encode non-ASCII in the body: `é`, `ë`, `ö`, `²`, `—` all garble (`é` becomes `√©`, `²` becomes `¬≤`). So when composing through macuse:

- Keep the body macuse types plain ASCII. A short Dutch cover note without accents reads fine and never garbles.
- Put anything with accents, figures, quotes, or real formatting into an attachment you generate yourself (PDF via HTML + headless Chrome, or DOCX), where you control the encoding. Verify the rendered file before attaching.
- Never leave a draft with mojibake sitting in Mail. If a character won't render cleanly in the body, move that text into the attachment.

Never em-dashes regardless; hyphens only.

## Sending

- Everything goes out as a draft first, never `send_immediately`. Read the draft back with `mail_get_messages` and check the sender address, the recipients and every attachment by filename and size. The compose tool has no From parameter, so the account name doesn't guarantee the sender, and attachments can drop or double.
- An outgoing mail carries only what the recipient can act on. No account of how the work was checked, no explaining their own field to them, no case for why the structure is clever. State facts and terms; the process story stays with me.
