import React, { useState } from 'react';
import { MapPin, Calendar, DollarSign } from 'lucide-react';

interface LocationFormProps {
  onSubmit: (location: string, days?: number, budget?: string) => void;
  isLoading: boolean;
}

export const LocationForm: React.FC<LocationFormProps> = ({ onSubmit, isLoading }) => {
  const [location, setLocation] = useState('');
  const [days, setDays] = useState<number | ''>('');
  const [budget, setBudget] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!location.trim()) return;
    onSubmit(location, days === '' ? undefined : Number(days), budget || undefined);
  };

  return (
    <div className="w-full max-w-md mx-auto p-6 bg-white rounded-xl shadow-lg">
      <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">去哪里玩？</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <MapPin className="absolute left-3 top-3 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="输入旅游地点 (如: 成都, 巴黎)"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
            required
          />
        </div>
        
        <div className="flex gap-4">
          <div className="relative flex-1">
            <Calendar className="absolute left-3 top-3 text-gray-400" size={20} />
            <input
              type="number"
              placeholder="天数 (可选)"
              value={days}
              onChange={(e) => setDays(e.target.value === '' ? '' : Number(e.target.value))}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
              min="1"
            />
          </div>
          <div className="relative flex-1">
            <DollarSign className="absolute left-3 top-3 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="预算 (可选)"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className={`w-full py-3 rounded-lg font-semibold text-white transition
            ${isLoading ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 shadow-md hover:shadow-lg'}`}
        >
          {isLoading ? '生成大纲中...' : '生成攻略大纲'}
        </button>
      </form>
    </div>
  );
};
