/**
 * Mindmap CLI Command Tests
 *
 * Tests the command parsing and node manipulation logic for:
 * - PARENT > CHILD (add child node)
 * - OLD = NEW (rename node)
 * - clear (empty mindmap)
 *
 * Run: node kore/tests/mindmap/cli.test.js
 */

// =============================================================================
// Core Functions (extracted from index.html for testing)
// =============================================================================

function findNode(node, text) {
  if (node.text.toLowerCase() === text.toLowerCase()) return node;
  for (const child of node.children || []) {
    const found = findNode(child, text);
    if (found) return found;
  }
  return null;
}

function addChildNode(mindmapData, parentText, childText) {
  if (!mindmapData) return false;

  const parent = findNode(mindmapData, parentText);
  if (!parent) return false;

  if (!parent.children) parent.children = [];
  parent.children.push({ text: childText, children: [] });
  return true;
}

function renameNode(mindmapData, oldText, newText) {
  if (!mindmapData) return false;

  const node = findNode(mindmapData, oldText);
  if (!node) return false;

  node.text = newText;
  return true;
}

function clearMindmap(mindmapData) {
  if (!mindmapData) return false;
  mindmapData.children = [];
  return true;
}

// Command parsing helpers
function parseCommand(cmd, mindmapData) {
  // Rename: OLD = NEW
  if (cmd.includes('=') && !cmd.includes('>')) {
    const [oldText, newText] = cmd.split('=').map(s => s.trim());
    if (oldText && newText) {
      return { type: 'rename', oldText, newText };
    }
  }

  // Add child: PARENT > CHILD
  if (cmd.includes('>')) {
    const [parent, child] = cmd.split('>').map(s => s.trim());
    if (parent && child) {
      return { type: 'addChild', parent, child };
    }
  }

  // Clear
  if (cmd.trim().toLowerCase() === 'clear') {
    return { type: 'clear' };
  }

  return null;
}

// =============================================================================
// Test Framework (minimal)
// =============================================================================

let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (condition) {
    passed++;
    console.log(`  ✓ ${message}`);
  } else {
    failed++;
    console.log(`  ✗ ${message}`);
  }
}

function assertEqual(actual, expected, message) {
  const isEqual = JSON.stringify(actual) === JSON.stringify(expected);
  if (isEqual) {
    passed++;
    console.log(`  ✓ ${message}`);
  } else {
    failed++;
    console.log(`  ✗ ${message}`);
    console.log(`    Expected: ${JSON.stringify(expected)}`);
    console.log(`    Actual:   ${JSON.stringify(actual)}`);
  }
}

function describe(name, fn) {
  console.log(`\n${name}`);
  fn();
}

// =============================================================================
// Tests
// =============================================================================

// Sample mindmap data
function createSampleMindmap() {
  return {
    text: 'IDEAS',
    children: [
      { text: 'Design', children: [] },
      { text: 'Code', children: [
        { text: 'Frontend', children: [] },
        { text: 'Backend', children: [] }
      ]},
      { text: 'Test', children: [] }
    ]
  };
}

describe('Command Parsing', () => {
  // Rename command
  assert(
    parseCommand('IDEAS = CONCEPTS').type === 'rename',
    'Detects rename command (OLD = NEW)'
  );
  assertEqual(
    parseCommand('IDEAS = CONCEPTS'),
    { type: 'rename', oldText: 'IDEAS', newText: 'CONCEPTS' },
    'Parses rename command correctly'
  );
  assertEqual(
    parseCommand('  Design  =  Architecture  '),
    { type: 'rename', oldText: 'Design', newText: 'Architecture' },
    'Trims whitespace in rename command'
  );

  // Add child command
  assert(
    parseCommand('IDEAS > NewChild').type === 'addChild',
    'Detects add child command (PARENT > CHILD)'
  );
  assertEqual(
    parseCommand('IDEAS > NewChild'),
    { type: 'addChild', parent: 'IDEAS', child: 'NewChild' },
    'Parses add child command correctly'
  );
  assertEqual(
    parseCommand('  Code  >  Database  '),
    { type: 'addChild', parent: 'Code', child: 'Database' },
    'Trims whitespace in add child command'
  );

  // Clear command
  assertEqual(
    parseCommand('clear'),
    { type: 'clear' },
    'Parses clear command'
  );
  assertEqual(
    parseCommand('CLEAR'),
    { type: 'clear' },
    'Clear command is case insensitive'
  );

  // Invalid commands
  assert(
    parseCommand('invalid') === null,
    'Returns null for invalid command'
  );
  assert(
    parseCommand('') === null,
    'Returns null for empty command'
  );
});

describe('findNode', () => {
  const data = createSampleMindmap();

  assert(
    findNode(data, 'IDEAS') !== null,
    'Finds root node'
  );
  assert(
    findNode(data, 'Design') !== null,
    'Finds first-level child'
  );
  assert(
    findNode(data, 'Frontend') !== null,
    'Finds nested child'
  );
  assert(
    findNode(data, 'ideas') !== null,
    'Search is case insensitive'
  );
  assert(
    findNode(data, 'NonExistent') === null,
    'Returns null for non-existent node'
  );
});

describe('addChildNode (PARENT > CHILD)', () => {
  let data = createSampleMindmap();

  assert(
    addChildNode(data, 'IDEAS', 'NewChild') === true,
    'Adds child to root node'
  );
  assert(
    findNode(data, 'NewChild') !== null,
    'New child is findable'
  );
  assertEqual(
    data.children.length,
    4,
    'Root now has 4 children'
  );

  data = createSampleMindmap();
  assert(
    addChildNode(data, 'Code', 'Database') === true,
    'Adds child to nested node'
  );
  const codeNode = findNode(data, 'Code');
  assertEqual(
    codeNode.children.length,
    3,
    'Code node now has 3 children'
  );

  assert(
    addChildNode(data, 'NonExistent', 'Child') === false,
    'Returns false for non-existent parent'
  );

  assert(
    addChildNode(null, 'IDEAS', 'Child') === false,
    'Returns false for null mindmap data'
  );
});

describe('renameNode (OLD = NEW)', () => {
  let data = createSampleMindmap();

  assert(
    renameNode(data, 'IDEAS', 'CONCEPTS') === true,
    'Renames root node'
  );
  assertEqual(
    data.text,
    'CONCEPTS',
    'Root text is updated'
  );

  data = createSampleMindmap();
  assert(
    renameNode(data, 'Frontend', 'UI') === true,
    'Renames nested node'
  );
  assert(
    findNode(data, 'UI') !== null,
    'Renamed node is findable by new name'
  );
  assert(
    findNode(data, 'Frontend') === null,
    'Old name no longer exists'
  );

  assert(
    renameNode(data, 'NonExistent', 'NewName') === false,
    'Returns false for non-existent node'
  );

  assert(
    renameNode(null, 'IDEAS', 'NewName') === false,
    'Returns false for null mindmap data'
  );
});

describe('clearMindmap', () => {
  let data = createSampleMindmap();

  assert(
    data.children.length > 0,
    'Initially has children'
  );
  assert(
    clearMindmap(data) === true,
    'Clear returns true'
  );
  assertEqual(
    data.children.length,
    0,
    'Children array is empty after clear'
  );
  assertEqual(
    data.text,
    'IDEAS',
    'Root text is preserved'
  );

  assert(
    clearMindmap(null) === false,
    'Returns false for null mindmap data'
  );
});

describe('Integration: Command sequence', () => {
  let data = createSampleMindmap();

  // Add a child
  const cmd1 = parseCommand('Test > Unit');
  addChildNode(data, cmd1.parent, cmd1.child);
  assert(
    findNode(data, 'Unit') !== null,
    'Added Unit under Test'
  );

  // Rename it
  const cmd2 = parseCommand('Unit = UnitTests');
  renameNode(data, cmd2.oldText, cmd2.newText);
  assert(
    findNode(data, 'UnitTests') !== null,
    'Renamed Unit to UnitTests'
  );

  // Add another child to renamed node
  const cmd3 = parseCommand('UnitTests > Jest');
  addChildNode(data, cmd3.parent, cmd3.child);
  assert(
    findNode(data, 'Jest') !== null,
    'Added Jest under renamed UnitTests'
  );

  // Clear everything
  clearMindmap(data);
  assertEqual(
    data.children.length,
    0,
    'Clear removed all children'
  );
});

// =============================================================================
// Summary
// =============================================================================

console.log('\n' + '='.repeat(50));
console.log(`Tests: ${passed + failed} | Passed: ${passed} | Failed: ${failed}`);
console.log('='.repeat(50));

process.exit(failed > 0 ? 1 : 0);
