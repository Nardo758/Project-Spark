import { useState, useEffect } from 'react';

interface CalendarData {
  days: number;
  calendar: Record<string, Record<string, number>>;
  source_totals: Record<string, number>;
  total_items: number;
  sources: string[];
}

const SOURCE_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  twitter: { bg: 'bg-blue-500/20', text: 'text-blue-400', border: 'border-blue-500' },
  reddit: { bg: 'bg-orange-500/20', text: 'text-orange-400', border: 'border-orange-500' },
  google_maps: { bg: 'bg-green-500/20', text: 'text-green-400', border: 'border-green-500' },
  yelp: { bg: 'bg-red-500/20', text: 'text-red-400', border: 'border-red-500' },
  craigslist: { bg: 'bg-purple-500/20', text: 'text-purple-400', border: 'border-purple-500' },
  custom: { bg: 'bg-gray-500/20', text: 'text-gray-400', border: 'border-gray-500' },
  nextdoor: { bg: 'bg-emerald-500/20', text: 'text-emerald-400', border: 'border-emerald-500' },
};

const getSourceColor = (source: string) => {
  return SOURCE_COLORS[source] || SOURCE_COLORS.custom;
};

export default function WebhookCalendar() {
  const [data, setData] = useState<CalendarData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);

  useEffect(() => {
    fetchCalendarData();
  }, []);

  const fetchCalendarData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/webhooks/calendar?days=30');
      if (!response.ok) throw new Error('Failed to fetch calendar data');
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const generateCalendarDays = () => {
    const days = [];
    const today = new Date();
    
    for (let i = 29; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      days.push({
        date: dateStr,
        dayOfWeek: date.getDay(),
        dayOfMonth: date.getDate(),
        month: date.toLocaleDateString('en-US', { month: 'short' }),
        isToday: i === 0,
      });
    }
    return days;
  };

  const calendarDays = generateCalendarDays();

  if (loading) {
    return (
      <div className="bg-stone-900 rounded-xl p-6 border border-stone-800">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-stone-800 rounded w-48"></div>
          <div className="grid grid-cols-7 gap-2">
            {Array(30).fill(0).map((_, i) => (
              <div key={i} className="h-16 bg-stone-800 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-stone-900 rounded-xl p-6 border border-red-800">
        <p className="text-red-400">Error: {error}</p>
        <button 
          onClick={fetchCalendarData}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="bg-stone-900 rounded-xl p-6 border border-stone-800">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-white">Webhook Run Calendar</h2>
          <p className="text-sm text-stone-400 mt-1">Last 30 days of data imports</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-2xl font-bold text-white">{data?.total_items.toLocaleString()}</p>
            <p className="text-xs text-stone-400">Total Items</p>
          </div>
          <button
            onClick={fetchCalendarData}
            className="p-2 text-stone-400 hover:text-white hover:bg-stone-800 rounded-lg transition-colors"
            title="Refresh"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-6">
        {data?.sources.map(source => {
          const colors = getSourceColor(source);
          const count = data.source_totals[source] || 0;
          return (
            <div 
              key={source}
              className={`px-3 py-1.5 rounded-full ${colors.bg} ${colors.text} border ${colors.border} text-sm font-medium flex items-center gap-2`}
            >
              <span className="capitalize">{source.replace('_', ' ')}</span>
              <span className="bg-black/30 px-2 py-0.5 rounded-full text-xs">{count.toLocaleString()}</span>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-7 gap-1 mb-2">
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
          <div key={day} className="text-center text-xs text-stone-500 py-1">{day}</div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-1">
        {calendarDays[0].dayOfWeek > 0 && 
          Array(calendarDays[0].dayOfWeek).fill(0).map((_, i) => (
            <div key={`empty-${i}`} className="h-20"></div>
          ))
        }
        
        {calendarDays.map(day => {
          const dayData = data?.calendar[day.date] || {};
          const hasData = Object.keys(dayData).length > 0;
          const totalCount = Object.values(dayData).reduce((sum, count) => sum + count, 0);
          
          return (
            <div
              key={day.date}
              onClick={() => setSelectedDate(selectedDate === day.date ? null : day.date)}
              className={`
                h-20 p-1.5 rounded-lg border cursor-pointer transition-all
                ${day.isToday ? 'border-blue-500 bg-blue-500/10' : 'border-stone-800 hover:border-stone-600'}
                ${selectedDate === day.date ? 'ring-2 ring-blue-500' : ''}
                ${hasData ? 'bg-stone-800/50' : ''}
              `}
            >
              <div className="flex items-start justify-between">
                <span className={`text-xs font-medium ${day.isToday ? 'text-blue-400' : 'text-stone-400'}`}>
                  {day.dayOfMonth === 1 ? `${day.month} ${day.dayOfMonth}` : day.dayOfMonth}
                </span>
                {totalCount > 0 && (
                  <span className="text-xs font-bold text-white bg-stone-700 px-1.5 rounded">
                    {totalCount}
                  </span>
                )}
              </div>
              
              <div className="flex flex-wrap gap-0.5 mt-1">
                {Object.entries(dayData).slice(0, 3).map(([source, count]) => {
                  const colors = getSourceColor(source);
                  return (
                    <div
                      key={source}
                      className={`w-full h-1.5 rounded-full ${colors.bg} ${colors.border} border`}
                      title={`${source}: ${count}`}
                    ></div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {selectedDate && data?.calendar[selectedDate] && (
        <div className="mt-4 p-4 bg-stone-800 rounded-lg border border-stone-700">
          <h3 className="text-white font-medium mb-3">
            {new Date(selectedDate + 'T00:00:00').toLocaleDateString('en-US', { 
              weekday: 'long', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {Object.entries(data.calendar[selectedDate]).map(([source, count]) => {
              const colors = getSourceColor(source);
              return (
                <div 
                  key={source}
                  className={`p-3 rounded-lg ${colors.bg} border ${colors.border}`}
                >
                  <p className={`text-sm capitalize ${colors.text}`}>{source.replace('_', ' ')}</p>
                  <p className="text-2xl font-bold text-white">{count.toLocaleString()}</p>
                  <p className="text-xs text-stone-400">items imported</p>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
