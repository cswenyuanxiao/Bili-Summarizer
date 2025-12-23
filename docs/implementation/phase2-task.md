# Phase 2: Component Migration Task List

## Component Structure
- [ ] Create `components/` directory structure
- [ ] Create `types/` directory for TypeScript definitions
- [ ] Create `composables/` directory for reusable logic

## Type Definitions
- [/] Create `types/api.ts` - API request/response types
- [ ] Create `types/history.ts` - History record types

## Core Components
- [/] `UrlInputCard.vue` - URL input form with mode/focus selectors
- [ ] `LoadingOverlay.vue` - Loading state with progress bar
- [ ] `SummaryCard.vue` - AI summary display with Markdown
- [ ] `TranscriptPanel.vue` - Video transcript display
- [ ] `MindmapViewer.vue` - Mermaid diagram viewer
- [ ] `ExportBar.vue` - Export buttons (PDF, MD, TXT, etc.)
- [ ] `HistoryList.vue` - History records grid
- [ ] `VideoPreview.vue` - Video thumbnail and info

## Composables
- [ ] `useSummarize.ts` - Summarization logic and SSE handling
- [ ] `useHistory.ts` - Local history management
- [ ] `useTheme.ts` - Theme toggle logic

## Integration
- [ ] Update `App.vue` to use all components
- [ ] Test component interactions
- [ ] Verify styling matches original design
