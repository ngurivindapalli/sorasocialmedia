import { Eye, Heart, ExternalLink } from 'lucide-react'

function VideoCard({ video, index }) {
  return (
    <div className="mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-2xl font-bold text-white">
          Video #{index + 1}
        </h3>
        <a
          href={video.video_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
        >
          <ExternalLink className="w-4 h-4" />
          View on X
        </a>
      </div>

      <div className="flex gap-6 mb-4">
        <div className="flex items-center gap-2 text-gray-300">
          <Eye className="w-5 h-5 text-blue-400" />
          <span className="font-semibold">{video.views.toLocaleString()}</span>
          <span className="text-sm">views</span>
        </div>
      </div>
    </div>
  )
}

export default VideoCard
