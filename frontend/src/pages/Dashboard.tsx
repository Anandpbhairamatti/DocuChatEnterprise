import { useEffect, useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { api } from '../api/axios';

export default function Dashboard() {
  const { user } = useAuthStore();
  const [docCount, setDocCount] = useState(0);
  const [chatCount, setChatCount] = useState(0);

  useEffect(() => {
    const fetchCounts = async () => {
      try {
        const [docsRes, chatsRes] = await Promise.all([
          api.get('/documents/'),
          api.get('/chat/')
        ]);
        setDocCount(docsRes.data.length);
        setChatCount(chatsRes.data.length);
      } catch (error) {
        console.error('Failed to fetch dashboard counts:', error);
      }
    };
    fetchCounts();
  }, []);
  
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Welcome, {user?.full_name}</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 bg-card border border-border rounded-xl shadow-sm">
          <h3 className="text-lg font-semibold mb-2">My Documents</h3>
          <p className="text-3xl font-bold text-primary">{docCount}</p>
        </div>
        <div className="p-6 bg-card border border-border rounded-xl shadow-sm">
          <h3 className="text-lg font-semibold mb-2">Recent Chats</h3>
          <p className="text-3xl font-bold text-primary">{chatCount}</p>
        </div>
        <div className="p-6 bg-card border border-border rounded-xl shadow-sm">
          <h3 className="text-lg font-semibold mb-2">System Status</h3>
          <p className="text-xl font-bold text-green-500">All Systems Operational</p>
        </div>
      </div>
    </div>
  );
}
