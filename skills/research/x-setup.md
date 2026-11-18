# Connecting the X MCP

X hosts an MCP server at `https://api.x.com/mcp` (docs: https://docs.x.com/tools/mcp). For research, read access is enough, so the app-only Bearer route works without the login bridge.

1. In the X Developer Portal (https://developer.x.com), create an app. Put it in the **Pay-per-use** package and the **Production** environment; otherwise the server answers `client-not-enrolled`.
2. Copy the app's **App-only Bearer token** from its 'Keys and tokens' page.
3. Add the server for every project:

   ```bash
   claude mcp add --scope user --transport http xapi https://api.x.com/mcp --header "Authorization: Bearer <token>"
   ```

4. Check it: `claude mcp list` shows `xapi` as connected.

The Bearer route is read-only and acts as no user. Bookmarks, Articles and anything in an account's name need the `xurl mcp` bridge with OAuth 2.0; see the docs.

Treat the token as a secret: it lives in the user-scope MCP config, never in a repo.
