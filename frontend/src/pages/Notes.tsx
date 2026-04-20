import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Plus, Search, Trash2, Edit2, Save, X, FileText } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

interface Note {
  id: string;
  title: string;
  content: string;
  createdAt: Date;
  updatedAt: Date;
}

const Notes = () => {
  const [notes, setNotes] = useState<Note[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isAdding, setIsAdding] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [newNote, setNewNote] = useState({ title: '', content: '' });
  const [editNote, setEditNote] = useState({ title: '', content: '' });

  // Load notes from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('anay_notes');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setNotes(parsed.map((n: any) => ({
          ...n,
          createdAt: new Date(n.createdAt),
          updatedAt: new Date(n.updatedAt),
        })));
      } catch (e) {
        console.error('Error loading notes:', e);
      }
    }
  }, []);

  // Save notes to localStorage
  useEffect(() => {
    if (notes.length > 0) {
      localStorage.setItem('anay_notes', JSON.stringify(notes));
    }
  }, [notes]);

  const filteredNotes = notes.filter(note =>
    note.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    note.content.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleAddNote = () => {
    if (newNote.title.trim() || newNote.content.trim()) {
      const now = new Date();
      const note: Note = {
        id: Date.now().toString(),
        title: newNote.title || 'Untitled',
        content: newNote.content,
        createdAt: now,
        updatedAt: now,
      };
      setNotes([note, ...notes]);
      setNewNote({ title: '', content: '' });
      setIsAdding(false);
    }
  };

  const handleStartEdit = (note: Note) => {
    setEditingId(note.id);
    setEditNote({ title: note.title, content: note.content });
  };

  const handleSaveEdit = (id: string) => {
    setNotes(notes.map(note =>
      note.id === id
        ? { ...note, title: editNote.title || 'Untitled', content: editNote.content, updatedAt: new Date() }
        : note
    ));
    setEditingId(null);
    setEditNote({ title: '', content: '' });
  };

  const handleDeleteNote = (id: string) => {
    setNotes(notes.filter(n => n.id !== id));
  };

  return (
    <div className="h-full flex flex-col gap-4 p-4">
      <Link to="/" className="text-xs font-orbitron text-muted-foreground hover:text-primary w-fit">
        ← Back to ANAY
      </Link>
      <div className="anay-panel p-4 flex flex-col gap-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-primary" />
            <h2 className="font-orbitron text-primary text-lg tracking-wider anay-glow-text">
              NOTES
            </h2>
          </div>
          <Button
            onClick={() => setIsAdding(!isAdding)}
            className="anay-button-secondary"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Note
          </Button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search notes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Add Note Form */}
        {isAdding && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="p-4 bg-secondary/30 rounded-lg space-y-3"
          >
            <Input
              placeholder="Title"
              value={newNote.title}
              onChange={(e) => setNewNote({ ...newNote, title: e.target.value })}
            />
            <Textarea
              placeholder="Write your note here..."
              value={newNote.content}
              onChange={(e) => setNewNote({ ...newNote, content: e.target.value })}
              rows={4}
            />
            <div className="flex gap-2">
              <Button onClick={handleAddNote} className="flex-1">
                <Save className="w-4 h-4 mr-2" />
                Save
              </Button>
              <Button
                onClick={() => {
                  setIsAdding(false);
                  setNewNote({ title: '', content: '' });
                }}
                variant="outline"
                className="flex-1"
              >
                <X className="w-4 h-4 mr-2" />
                Cancel
              </Button>
            </div>
          </motion.div>
        )}
      </div>

      {/* Notes List */}
      <div className="flex-1 anay-panel overflow-hidden flex flex-col">
        <div className="p-4 border-b border-border/30">
          <span className="text-xs text-muted-foreground font-orbitron">
            {filteredNotes.length} NOTE{filteredNotes.length !== 1 ? 'S' : ''}
          </span>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {filteredNotes.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>No notes found</p>
              {notes.length === 0 && (
                <p className="text-xs mt-1">Create your first note to get started</p>
              )}
            </div>
          ) : (
            filteredNotes.map((note, index) => (
              <motion.div
                key={note.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="bg-secondary/30 rounded-lg p-4 hover:bg-secondary/50 transition-colors"
              >
                {editingId === note.id ? (
                  <div className="space-y-3">
                    <Input
                      value={editNote.title}
                      onChange={(e) => setEditNote({ ...editNote, title: e.target.value })}
                    />
                    <Textarea
                      value={editNote.content}
                      onChange={(e) => setEditNote({ ...editNote, content: e.target.value })}
                      rows={4}
                    />
                    <div className="flex gap-2">
                      <Button onClick={() => handleSaveEdit(note.id)} size="sm" className="flex-1">
                        <Save className="w-3 h-3 mr-1" />
                        Save
                      </Button>
                      <Button
                        onClick={() => {
                          setEditingId(null);
                          setEditNote({ title: '', content: '' });
                        }}
                        variant="outline"
                        size="sm"
                        className="flex-1"
                      >
                        <X className="w-3 h-3 mr-1" />
                        Cancel
                      </Button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-orbitron text-foreground flex-1">{note.title}</h3>
                      <div className="flex gap-1">
                        <Button
                          onClick={() => handleStartEdit(note)}
                          variant="ghost"
                          size="sm"
                        >
                          <Edit2 className="w-3 h-3" />
                        </Button>
                        <Button
                          onClick={() => handleDeleteNote(note.id)}
                          variant="ghost"
                          size="sm"
                          className="text-destructive hover:text-destructive"
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground whitespace-pre-wrap mb-2">
                      {note.content || <span className="italic">No content</span>}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(note.updatedAt).toLocaleDateString()} {new Date(note.updatedAt).toLocaleTimeString()}
                    </p>
                  </>
                )}
              </motion.div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default Notes;
