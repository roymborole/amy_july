class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.data = None

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, data):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.data = data

    def search_prefix(self, prefix):
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]
        return self._dfs(node, prefix)

    def _dfs(self, node, prefix):
        result = []
        if node.is_end:
            result.append((prefix, node.data))
        for char, child in node.children.items():
            result.extend(self._dfs(child, prefix + char))
        return result