import { useState, useEffect, useRef } from 'react';
import { api } from '../api/axios';
import { Trash2 } from 'lucide-react';
import { useAuthStore } from '../store/authStore';

interface Document {
  id: string;
  original_name: string;
  status: string;
  size_bytes: number;
  uploaded_at: string;
  visibility: string;
  owner_id: string;
}

export default function Documents() {
  const { user } = useAuthStore();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  
  const [showModal, setShowModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [visibility, setVisibility] = useState('ORGANIZATION');
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchDocuments = async () => {
    try {
      const response = await api.get('/documents/');
      setDocuments(response.data);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
    // Poll for status updates every 5 seconds
    const interval = setInterval(fetchDocuments, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setShowModal(true);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('visibility', visibility);

    try {
      await api.post('/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      fetchDocuments();
      setShowModal(false);
      setSelectedFile(null);
    } catch (error: any) {
      console.error('Upload failed:', error);
      alert(`Upload failed: ${error.response?.data?.detail || 'Please try again.'}`);
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDeleteDocument = async (docId: string) => {
    if (!confirm('Are you sure you want to delete this document? This will permanently remove its AI knowledge context.')) return;
    
    try {
      await api.delete(`/documents/${docId}`);
      fetchDocuments();
    } catch (error: any) {
      console.error('Failed to delete document:', error);
      alert(`Failed to delete document: ${error.response?.data?.detail || 'Please try again.'}`);
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED': return 'bg-green-100 text-green-700';
      case 'PROCESSING': return 'bg-blue-100 text-blue-700';
      case 'QUEUED': return 'bg-yellow-100 text-yellow-700';
      case 'FAILED': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Document Management</h1>
        <input 
          type="file" 
          className="hidden" 
          ref={fileInputRef} 
          onChange={handleFileChange}
        />
        <button 
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="bg-primary text-primary-foreground px-4 py-2 rounded-md font-medium disabled:opacity-50 flex items-center gap-2 hover:opacity-90 transition-opacity"
        >
          Upload Document
        </button>
      </div>
      
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card p-6 rounded-xl shadow-lg w-full max-w-md">
            <h2 className="text-xl font-semibold mb-4">Upload Document</h2>
            <p className="text-sm text-muted-foreground mb-4">
              File: <span className="font-medium text-foreground">{selectedFile?.name}</span>
            </p>
            
            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">Visibility Level</label>
              <select 
                value={visibility}
                onChange={(e) => setVisibility(e.target.value)}
                className="w-full p-2 border border-border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="PRIVATE">PRIVATE (Only you and Admins)</option>
                <option value="DEPARTMENT">DEPARTMENT (Your department only)</option>
                <option value="ORGANIZATION">ORGANIZATION (Everyone)</option>
                <option value="RESTRICTED">RESTRICTED (Admins/Managers only)</option>
              </select>
            </div>
            
            <div className="flex justify-end gap-3">
              <button 
                onClick={() => {
                  setShowModal(false);
                  setSelectedFile(null);
                  if (fileInputRef.current) fileInputRef.current.value = '';
                }}
                className="px-4 py-2 text-sm font-medium border border-border rounded-md hover:bg-muted"
                disabled={uploading}
              >
                Cancel
              </button>
              <button 
                onClick={handleUpload}
                disabled={uploading}
                className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-md hover:opacity-90 flex items-center gap-2"
              >
                {uploading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin"></div>
                    Uploading...
                  </>
                ) : 'Upload'}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-muted/50 border-b border-border text-muted-foreground text-sm">
              <th className="p-4 font-medium">Name</th>
              <th className="p-4 font-medium">Visibility</th>
              <th className="p-4 font-medium">Status</th>
              <th className="p-4 font-medium">Size</th>
              <th className="p-4 font-medium">Uploaded</th>
              <th className="p-4 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading && documents.length === 0 ? (
              <tr>
                <td colSpan={6} className="p-8 text-center text-muted-foreground">Loading documents...</td>
              </tr>
            ) : documents.length === 0 ? (
              <tr>
                <td colSpan={6} className="p-8 text-center text-muted-foreground">No documents uploaded yet.</td>
              </tr>
            ) : (
              documents.map((doc) => (
                <tr key={doc.id} className="border-b border-border/50 hover:bg-muted/20 transition-colors">
                  <td className="p-4 font-medium">{doc.original_name}</td>
                  <td className="p-4">
                    <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-md border border-gray-200">
                      {doc.visibility}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(doc.status)}`}>
                      {doc.status}
                    </span>
                  </td>
                  <td className="p-4 text-muted-foreground">{formatSize(doc.size_bytes)}</td>
                  <td className="p-4 text-muted-foreground">{new Date(doc.uploaded_at).toLocaleDateString()}</td>
                  <td className="p-4 text-right">
                    {(doc.owner_id === user?.id || user?.role === 'Admin') && (
                      <button
                        onClick={() => handleDeleteDocument(doc.id)}
                        className="p-2 text-muted-foreground hover:text-destructive transition-colors rounded-md hover:bg-destructive/10"
                        title="Delete Document"
                      >
                        <Trash2 size={18} />
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
