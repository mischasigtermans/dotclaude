---
name: mail
description: "Composing mail through Apple Mail via macuse. Use when drafting, replying to, or forwarding an email in Apple Mail. Covers the double-encoding bug that garbles accented characters and the attachment workaround. Triggers on 'draft an email', 'reply to this email', 'forward that email', 'write a mail to', 'stuur een mail'."
---

# Mail

Whatever lands in a Mail draft must be clean: no mojibake (garbled characters), no stray characters. The user's own writing rules apply to every word.

The macuse Apple Mail tools (`mail_reply_message`, `mail_compose_message`, `mail_forward_message`) double-encode non-ASCII in the body: `é`, `ë`, `ö`, `²`, `—` all garble (`é` becomes `√©`, `²` becomes `¬≤`). So when composing through macuse:

- Keep the body macuse types plain ASCII. A short cover note without accents reads fine and never garbles.
- Put anything with accents, figures, quotes or real formatting into an attachment you generate yourself (PDF via HTML + headless Chrome, or DOCX), where you control the encoding. Check the rendered file before you attach it.
- If a character won't render cleanly in the body, move that text into the attachment.

## Before the draft

Write the body and any attachment text first, then call the Skill tool with `writing`: draft in its personal mode, since the mail goes out in the user's name, and run its sharpen mode in self-check over the result. Fix every hit before a compose tool is called: a draft in Mail is already past the copy gate, which only sees files. A mail the user wrote or dictated word for word gets the diagnosis instead, never a silent rewrite.

## Sending

- Create every mail as a draft first; never use `send_immediately`. Read the draft back with `mail_get_messages` and check the sender address, the recipients and every attachment by filename and size. The compose tool has no From parameter, so the account name doesn't guarantee the sender, and attachments can drop or double.
- An outgoing mail carries only what the recipient can act on. Leave out how the work was checked, any explanation of their own field and any case for why the structure is clever. State facts and terms; the process story stays with the user.
