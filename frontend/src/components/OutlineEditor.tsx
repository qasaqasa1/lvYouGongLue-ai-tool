import React, { useState } from 'react';
import { OutlineNode } from '../types';
import { ChevronRight, ChevronDown, Plus, Trash2, GripVertical, Type, CornerDownRight } from 'lucide-react';

interface OutlineEditorProps {
  nodes: OutlineNode[];
  onChange: (nodes: OutlineNode[]) => void;
}

export const OutlineEditor: React.FC<OutlineEditorProps> = ({ nodes, onChange }) => {
  const handleUpdateNode = (id: string, updates: Partial<OutlineNode>) => {
    const updateRecursive = (currentNodes: OutlineNode[]): OutlineNode[] => {
      return currentNodes.map(node => {
        if (node.id === id) {
          return { ...node, ...updates };
        }
        if (node.children.length > 0) {
          return { ...node, children: updateRecursive(node.children) };
        }
        return node;
      });
    };
    onChange(updateRecursive(nodes));
  };

  const handleAddChild = (parentId: string) => {
    const addRecursive = (currentNodes: OutlineNode[]): OutlineNode[] => {
      return currentNodes.map(node => {
        if (node.id === parentId) {
          const newChild: OutlineNode = {
            id: Math.random().toString(36).substr(2, 9),
            title: '新标题',
            level: node.level + 1,
            children: []
          };
          return { ...node, children: [...node.children, newChild] };
        }
        if (node.children.length > 0) {
          return { ...node, children: addRecursive(node.children) };
        }
        return node;
      });
    };
    onChange(addRecursive(nodes));
  };

  const handleDeleteNode = (id: string) => {
    const deleteRecursive = (currentNodes: OutlineNode[]): OutlineNode[] => {
      return currentNodes.filter(node => node.id !== id).map(node => ({
        ...node,
        children: deleteRecursive(node.children)
      }));
    };
    onChange(deleteRecursive(nodes));
  };
  
  const handleAddSibling = (id: string) => {
      // Find parent of this node and add sibling
      // This is tricky with recursive structure without parent pointer.
      // Easier implementation: Pass a path or handle at the parent level.
      // Alternatively, we can traverse to find the parent.
      
      const addSiblingRecursive = (currentNodes: OutlineNode[]): OutlineNode[] => {
          // Check if the target node is in this list
          const index = currentNodes.findIndex(n => n.id === id);
          if (index !== -1) {
              const sibling: OutlineNode = {
                  id: Math.random().toString(36).substr(2, 9),
                  title: '新标题',
                  level: currentNodes[index].level,
                  children: []
              };
              const newNodes = [...currentNodes];
              newNodes.splice(index + 1, 0, sibling);
              return newNodes;
          }
          
          return currentNodes.map(node => ({
              ...node,
              children: addSiblingRecursive(node.children)
          }));
      };
      
      onChange(addSiblingRecursive(nodes));
  };

  return (
    <div className="space-y-2">
      {nodes.map(node => (
        <OutlineNodeItem
          key={node.id}
          node={node}
          onUpdate={handleUpdateNode}
          onAddChild={handleAddChild}
          onDelete={handleDeleteNode}
          onAddSibling={handleAddSibling}
        />
      ))}
      <button 
        onClick={() => {
             const newNode: OutlineNode = {
                id: Math.random().toString(36).substr(2, 9),
                title: '新顶级标题',
                level: 1,
                children: []
              };
              onChange([...nodes, newNode]);
        }}
        className="w-full py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-blue-500 hover:text-blue-500 transition flex items-center justify-center gap-2"
      >
        <Plus size={16} /> 添加顶级标题
      </button>
    </div>
  );
};

interface NodeItemProps {
  node: OutlineNode;
  onUpdate: (id: string, updates: Partial<OutlineNode>) => void;
  onAddChild: (id: string) => void;
  onDelete: (id: string) => void;
  onAddSibling: (id: string) => void;
}

const OutlineNodeItem: React.FC<NodeItemProps> = ({ node, onUpdate, onAddChild, onDelete, onAddSibling }) => {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className="ml-4">
      <div className={`flex items-center gap-2 p-2 rounded-lg hover:bg-gray-50 group ${node.level === 1 ? 'bg-gray-50 mb-2' : ''}`}>
        <button 
          onClick={() => setIsExpanded(!isExpanded)}
          className={`p-1 hover:bg-gray-200 rounded ${node.children.length === 0 ? 'invisible' : ''}`}
        >
          {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        </button>
        
        <div className="flex-1 flex items-center gap-2">
            <span className="text-xs font-mono text-gray-400">H{node.level}</span>
            <input
                type="text"
                value={node.title}
                onChange={(e) => onUpdate(node.id, { title: e.target.value })}
                className="flex-1 bg-transparent border-none outline-none focus:ring-2 focus:ring-blue-200 rounded px-1 font-medium"
                style={{ fontSize: node.level === 1 ? '1.1rem' : '1rem' }}
            />
        </div>

        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button onClick={() => onAddSibling(node.id)} className="p-1 hover:text-blue-600" title="添加同级">
                <Plus size={16} />
            </button>
            <button onClick={() => onAddChild(node.id)} className="p-1 hover:text-green-600" title="添加子级">
                <CornerDownRight size={16} />
            </button>
            <button onClick={() => onDelete(node.id)} className="p-1 hover:text-red-600" title="删除">
                <Trash2 size={16} />
            </button>
        </div>
      </div>

      {isExpanded && node.children.length > 0 && (
        <div className="border-l-2 border-gray-100 ml-3">
          {node.children.map(child => (
            <OutlineNodeItem
              key={child.id}
              node={child}
              onUpdate={onUpdate}
              onAddChild={onAddChild}
              onDelete={onDelete}
              onAddSibling={onAddSibling}
            />
          ))}
        </div>
      )}
    </div>
  );
};
