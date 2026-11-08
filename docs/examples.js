// One catalogue for navigation, URLs and review instructions.
export const examples = [
  {
    id: "loading",
    name: "Loading content",
    description: "Keep the layout in place while content arrives.",
    action: "Load projects",
    hint: "Load the projects. Both versions take 2.4 seconds.",
    benefit:
      "A recognisable layout makes the wait understandable and prevents content from jumping.",
  },
  {
    id: "loader",
    name: "Loading indicator",
    description: "Make an unknown wait feel responsive.",
    action: "Prepare preview",
    hint: "Prepare a preview. Unknown progress stays indeterminate.",
    benefit:
      "A small, continuous signal answers “is it still working?” without pretending to know the duration.",
  },
  {
    id: "slow",
    name: "Slow connection",
    description: "Explain a longer wait and offer a way out.",
    action: "Start slow load",
    hint: "Start the six-second load. Wait for the message, or cancel.",
    benefit:
      "Reassure people only when the wait becomes unusually long, and honour cancellation.",
  },
  {
    id: "offline",
    name: "Connection recovery",
    description: "Keep the work visible when the connection drops.",
    action: "Lose connection",
    hint: "Edit the note, disconnect, then restore the connection.",
    benefit:
      "Connection problems should not erase context or force someone to start again.",
  },
  {
    id: "upload",
    name: "File upload",
    description: "Show real progress and give people control.",
    action: "Upload demo file",
    hint: "Try pause, resume and cancel while progress is running.",
    benefit:
      "Progress follows completed work. Pausing freezes it; cancellation prevents late updates.",
  },
  {
    id: "save",
    name: "Saving changes",
    description: "A clear journey from editing to saved.",
    action: "Play save example",
    hint: "Edit the title and save, or play the full sequence.",
    benefit:
      "The control changes from Save to Saving to a confirmed check. Edits made during a save remain a draft.",
  },
  {
    id: "filter",
    name: "List filtering",
    description: "Help the eye follow a changing collection.",
    action: "Filter projects",
    hint: "Filter by status. Follow the rows that stay.",
    benefit:
      "Layout continuity makes it clear which items stayed, instead of making the entire list appear to change.",
  },
  {
    id: "toast",
    name: "Notifications",
    description: "Confirm an action, then leave quietly.",
    action: "Show notification",
    hint: "Show a notification. Focus or hover to keep it visible.",
    benefit:
      "A concise confirmation provides closure without moving the page or blocking a control.",
  },
  {
    id: "panel",
    name: "Side panel",
    description: "Make a new layer feel connected to its source.",
    action: "Open details",
    hint: "Open details. Try editing the note, then press Escape.",
    benefit:
      "A short entrance explains where the panel came from. Focus and unfinished input survive closing.",
  },
  {
    id: "tabs",
    name: "Tab transitions",
    description: "Move between views without an abrupt cut.",
    action: "Switch view",
    hint: "Change tabs with a click or the left and right arrow keys.",
    benefit:
      "A shared indicator and restrained content transition make the change of context easy to follow.",
  },
];
export function resolveExample(value) {
  return (
    examples.find(
      (item) =>
        item.id === ({ dispatch: "save", studio: "filter" }[value] || value),
    ) || examples[0]
  );
}
