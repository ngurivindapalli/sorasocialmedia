import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  Calendar, FileText, Video, Image, MessageSquare, 
  BarChart, Users, Megaphone, ChevronRight, Play
} from 'lucide-react'
import { contentCalendar, weekThemes } from '../data/contentCalendar'

function ContentCalendar() {
  const navigate = useNavigate()
  const [selectedWeek, setSelectedWeek] = useState(null)

  const getFormatIcon = (format) => {
    if (format.includes('Video')) return <Video className="w-4 h-4" />
    if (format.includes('Carousel')) return <Image className="w-4 h-4" />
    if (format.includes('Thread') || format.includes('Long Post')) return <FileText className="w-4 h-4" />
    if (format.includes('Poll')) return <BarChart className="w-4 h-4" />
    if (format.includes('Engagement') || format.includes('Community')) return <Users className="w-4 h-4" />
    if (format.includes('Announcement') || format.includes('Paid')) return <Megaphone className="w-4 h-4" />
    return <MessageSquare className="w-4 h-4" />
  }

  const getFormatColor = (format, isVideo) => {
    if (isVideo) return 'bg-amber-100 text-amber-700 border-amber-200'
    if (format.includes('Carousel')) return 'bg-purple-100 text-purple-700 border-purple-200'
    if (format.includes('Thread') || format.includes('Long Post') || format.includes('Field Note')) return 'bg-blue-100 text-blue-700 border-blue-200'
    if (format.includes('Poll')) return 'bg-green-100 text-green-700 border-green-200'
    if (format.includes('Engagement') || format.includes('Community')) return 'bg-pink-100 text-pink-700 border-pink-200'
    if (format.includes('Case Study')) return 'bg-teal-100 text-teal-700 border-teal-200'
    return 'bg-gray-100 text-gray-700 border-gray-200'
  }

  const weeks = [1, 2, 3, 4]
  const filteredContent = selectedWeek 
    ? contentCalendar.filter(c => c.week === selectedWeek)
    : contentCalendar

  return (
    <div className="min-h-screen bg-white p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Calendar className="w-8 h-8 text-[#1e293b]" />
            <h1 className="text-3xl font-bold text-[#111827]">30-Day Content Calendar</h1>
          </div>
          <p className="text-[#6b7280]">
            AIGIS Operator Field Notes Series — Foundation, Education, Credibility & Scale
          </p>
        </div>

        {/* Week Filter */}
        <div className="bg-white border border-[#e5e7eb] rounded-lg p-4 mb-6">
          <div className="flex flex-wrap items-center gap-3">
            <span className="text-sm font-medium text-[#6b7280]">Filter by Week:</span>
            <button
              onClick={() => setSelectedWeek(null)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedWeek === null
                  ? 'bg-[#1e293b] text-white'
                  : 'bg-[#f5f5f5] text-[#4b5563] hover:bg-[#e5e7eb]'
              }`}
            >
              All Weeks
            </button>
            {weeks.map(week => (
              <button
                key={week}
                onClick={() => setSelectedWeek(week)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedWeek === week
                    ? 'bg-[#1e293b] text-white'
                    : 'bg-[#f5f5f5] text-[#4b5563] hover:bg-[#e5e7eb]'
                }`}
              >
                Week {week}: {weekThemes[week].name}
              </button>
            ))}
          </div>
        </div>

        {/* Week Sections */}
        {weeks.filter(w => selectedWeek === null || w === selectedWeek).map(week => (
          <div key={week} className="mb-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-[#1e293b] text-white flex items-center justify-center font-bold">
                {week}
              </div>
              <div>
                <h2 className="text-xl font-semibold text-[#111827]">Week {week}: {weekThemes[week].name}</h2>
                <p className="text-sm text-[#6b7280]">{weekThemes[week].description}</p>
              </div>
            </div>

            <div className="grid gap-3">
              {contentCalendar.filter(c => c.week === week).map(content => (
                <div
                  key={content.day}
                  onClick={() => navigate(`/content-calendar/day/${content.day}`)}
                  className="bg-white border border-[#e5e7eb] rounded-lg p-4 hover:shadow-md transition-all cursor-pointer group"
                >
                  <div className="flex items-start gap-4">
                    {/* Day Number */}
                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center font-bold text-lg ${
                      content.isVideo ? 'bg-amber-100 text-amber-700' : 'bg-[#f5f5f5] text-[#4b5563]'
                    }`}>
                      {content.day}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium border ${getFormatColor(content.format, content.isVideo)}`}>
                          {getFormatIcon(content.format)}
                          {content.format}
                        </span>
                        {content.isVideo && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-amber-50 text-amber-600 border border-amber-200">
                            <Play className="w-3 h-3" />
                            Hand-generated
                          </span>
                        )}
                      </div>
                      <h3 className="text-[#111827] font-medium mb-1 truncate group-hover:text-[#1e293b]">
                        {content.headline}
                      </h3>
                      <p className="text-sm text-[#6b7280] truncate">
                        CTA: {content.cta}
                      </p>
                    </div>

                    {/* Arrow */}
                    <ChevronRight className="w-5 h-5 text-[#9ca3af] group-hover:text-[#1e293b] transition-colors" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}

        {/* Legend */}
        <div className="mt-8 p-4 bg-[#f9fafb] rounded-lg">
          <h3 className="font-medium text-[#111827] mb-3">Content Type Legend</h3>
          <div className="flex flex-wrap gap-3">
            <span className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700 border border-gray-200">
              <MessageSquare className="w-3 h-3" /> Text + Image
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-amber-100 text-amber-700 border border-amber-200">
              <Video className="w-3 h-3" /> Video (Hand-generated)
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-700 border border-purple-200">
              <Image className="w-3 h-3" /> Carousel
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-700 border border-blue-200">
              <FileText className="w-3 h-3" /> Thread / Field Note
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-700 border border-green-200">
              <BarChart className="w-3 h-3" /> Poll
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-pink-100 text-pink-700 border border-pink-200">
              <Users className="w-3 h-3" /> Engagement / Community
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-teal-100 text-teal-700 border border-teal-200">
              <FileText className="w-3 h-3" /> Case Study
            </span>
          </div>
        </div>

        {/* Stats */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white border border-[#e5e7eb] rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-[#111827]">30</div>
            <div className="text-sm text-[#6b7280]">Total Days</div>
          </div>
          <div className="bg-white border border-[#e5e7eb] rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-[#111827]">{contentCalendar.filter(c => !c.isVideo).length}</div>
            <div className="text-sm text-[#6b7280]">Image Posts</div>
          </div>
          <div className="bg-white border border-[#e5e7eb] rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-amber-600">{contentCalendar.filter(c => c.isVideo).length}</div>
            <div className="text-sm text-[#6b7280]">Video Posts</div>
          </div>
          <div className="bg-white border border-[#e5e7eb] rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-[#111827]">4</div>
            <div className="text-sm text-[#6b7280]">Field Notes</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ContentCalendar
