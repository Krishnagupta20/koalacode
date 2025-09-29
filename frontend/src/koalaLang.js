import * as monaco from "monaco-editor";

export function registerKoalaLanguage() {
  // Register Koala language
  monaco.languages.register({ id: "koala" });

  // Define tokens/keywords
  monaco.languages.setMonarchTokensProvider("koala", {
    tokenizer: {
      root: [
        // keywords
        [
          /\b(give|take|this|otherwise|iter|iter2|func|return)\b/,
          "keyword",
        ],

        // booleans
        [/\b(true|false)\b/, "constant.boolean"],

        // numbers
        [/[0-9]+/, "number"],

        // strings
        [/"([^"\\]|\\.)*$/, "string.invalid"], // non-terminated
        [/"/, { token: "string.quote", bracket: "@open", next: "@string" }],

        // function names (identifier followed by a parenthesis)
        [/[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()/, "function"],

        // identifiers (variables)
        [/[a-zA-Z_][a-zA-Z0-9_]*/, "identifier"],

        // brackets
        [/[{}()\[\]]/, "@brackets"],

        // comments
        [/#.*$/, "comment"],
      ],

      string: [
        [/[^\\"]+/, "string"],
        [/\\./, "string.escape"],
        [/"/, { token: "string.quote", bracket: "@close", next: "@pop" }],
      ],
    },
  });

  // Define editor theme
  monaco.editor.defineTheme("koalaTheme", {
    base: "vs-dark",
    inherit: true,
    rules: [
      { token: "keyword", foreground: "ff9d00", fontStyle: "bold" }, // orange keywords
      { token: "constant.boolean", foreground: "56b6c2", fontStyle: "bold" }, // teal booleans
      { token: "number", foreground: "d19a66" }, // amber numbers
      { token: "string", foreground: "98c379" }, // green strings
      { token: "string.escape", foreground: "e06c75" }, // red escapes
      { token: "comment", foreground: "5c6370", fontStyle: "italic" }, // gray comments
      { token: "function", foreground: "61afef" }, // blue functions
      { token: "identifier", foreground: "ffffff" }, // white identifiers
    ],
    colors: {
      "editor.background": "#1e1e1e",
      "editorLineNumber.foreground": "#858585",
      "editorCursor.foreground": "#ffffff",
      "editorBracketMatch.border": "#ffd700",
    },
  });
}
