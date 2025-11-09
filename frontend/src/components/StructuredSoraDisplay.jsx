import { useState } from 'react';

/**
 * Enhanced display for Structured Sora Scripts (OpenAI Build Hours - Structured Outputs)
 * Shows validated, consistent format with all sections
 */
export default function StructuredSoraDisplay({ result }) {
  const [showStructured, setShowStructured] = useState(true);
  const structured = result.structured_sora_script;
  const thumbnail = result.thumbnail_analysis;

  // If no structured script, show the basic sora_script
  if (!structured) {
    return (
      <div className="bg-gradient-to-br from-purple-900/30 to-pink-900/30 rounded-lg p-6 border border-pink-500/30">
        <p className="text-gray-100 text-sm leading-relaxed whitespace-pre-wrap">
          {result.sora_script}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Toggle between structured and legacy format */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setShowStructured(true)}
          className={`px-4 py-2 rounded-lg font-medium transition-all ${
            showStructured
              ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg'
              : 'bg-white/10 text-gray-400 hover:bg-white/20'
          }`}
        >
          📊 Structured Output (Build Hours)
        </button>
        <button
          onClick={() => setShowStructured(false)}
          className={`px-4 py-2 rounded-lg font-medium transition-all ${
            !showStructured
              ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg'
              : 'bg-white/10 text-gray-400 hover:bg-white/20'
          }`}
        >
          📝 Legacy Format
        </button>
      </div>

      {showStructured ? (
        <div className="space-y-6">
          {/* Vision API Thumbnail Analysis */}
          {thumbnail && (
            <div className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/30 rounded-xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-2xl">👁️</span>
                <h4 className="text-xl font-bold text-blue-300">Vision API Analysis</h4>
                <span className="ml-auto text-xs bg-blue-500/20 px-3 py-1 rounded-full text-blue-300">
                  GPT-4 Vision
                </span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-sm text-gray-400 mb-2">Dominant Colors</p>
                  <div className="flex flex-wrap gap-2">
                    {thumbnail.dominant_colors.map((color, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-blue-500/20 rounded-full text-sm text-blue-200"
                      >
                        {color}
                      </span>
                    ))}
                  </div>
                </div>
                
                <div>
                  <p className="text-sm text-gray-400 mb-2">Visual Elements</p>
                  <div className="flex flex-wrap gap-2">
                    {thumbnail.visual_elements.map((element, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-cyan-500/20 rounded-full text-sm text-cyan-200"
                      >
                        {element}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              
              <div className="space-y-2">
                <div>
                  <p className="text-sm text-gray-400">Composition</p>
                  <p className="text-gray-200">{thumbnail.composition}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-400">Style Assessment</p>
                  <p className="text-gray-200">{thumbnail.style_assessment}</p>
                </div>
              </div>
            </div>
          )}

          {/* Core Concept */}
          <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/30 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">🎯</span>
              <h4 className="text-xl font-bold text-purple-300">Core Concept</h4>
            </div>
            <p className="text-gray-200 leading-relaxed">{structured.core_concept}</p>
          </div>

          {/* Visual Style */}
          <div className="bg-gradient-to-br from-pink-500/10 to-rose-500/10 border border-pink-500/30 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-2xl">🎨</span>
              <h4 className="text-xl font-bold text-pink-300">Visual Style</h4>
            </div>
            
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-400 mb-2">Colors</p>
                <div className="flex flex-wrap gap-2">
                  {structured.visual_style.primary_colors.map((color, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-pink-500/20 rounded-full text-sm text-pink-200"
                    >
                      {color}
                    </span>
                  ))}
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-400">Lighting</p>
                  <p className="text-gray-200">{structured.visual_style.lighting}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-400">Mood</p>
                  <p className="text-gray-200">{structured.visual_style.mood}</p>
                </div>
              </div>
              
              <div>
                <p className="text-sm text-gray-400">Visual References</p>
                <p className="text-gray-200">{structured.visual_style.visual_references}</p>
              </div>
            </div>
          </div>

          {/* Camera Work */}
          <div className="bg-gradient-to-br from-indigo-500/10 to-blue-500/10 border border-indigo-500/30 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-2xl">🎥</span>
              <h4 className="text-xl font-bold text-indigo-300">Camera Work</h4>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-400 mb-2">Shot Types</p>
                <div className="space-y-1">
                  {structured.camera_work.shot_types.map((shot, idx) => (
                    <div key={idx} className="text-sm text-gray-200 flex items-center gap-2">
                      <span className="text-indigo-400">▸</span> {shot}
                    </div>
                  ))}
                </div>
              </div>
              
              <div>
                <p className="text-sm text-gray-400 mb-2">Movements</p>
                <div className="space-y-1">
                  {structured.camera_work.camera_movements.map((movement, idx) => (
                    <div key={idx} className="text-sm text-gray-200 flex items-center gap-2">
                      <span className="text-indigo-400">▸</span> {movement}
                    </div>
                  ))}
                </div>
              </div>
              
              <div>
                <p className="text-sm text-gray-400 mb-2">Angles</p>
                <div className="space-y-1">
                  {structured.camera_work.angles.map((angle, idx) => (
                    <div key={idx} className="text-sm text-gray-200 flex items-center gap-2">
                      <span className="text-indigo-400">▸</span> {angle}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Timing & Pacing */}
          <div className="bg-gradient-to-br from-emerald-500/10 to-teal-500/10 border border-emerald-500/30 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-2xl">⏱️</span>
              <h4 className="text-xl font-bold text-emerald-300">Timing & Pacing</h4>
            </div>
            
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-400">Duration</p>
                  <p className="text-gray-200 font-semibold">{structured.timing.total_duration}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-400">Pacing</p>
                  <p className="text-gray-200 font-semibold">{structured.timing.pacing}</p>
                </div>
              </div>
              
              <div>
                <p className="text-sm text-gray-400 mb-2">Key Moments</p>
                <div className="space-y-1">
                  {structured.timing.key_moments.map((moment, idx) => (
                    <div key={idx} className="text-sm text-gray-200 flex items-center gap-2">
                      <span className="text-emerald-400">▸</span> {moment}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Full Sora Prompt */}
          <div className="bg-gradient-to-br from-orange-500/10 to-amber-500/10 border border-orange-500/30 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">✨</span>
              <h4 className="text-xl font-bold text-orange-300">Complete Sora Prompt</h4>
            </div>
            <p className="text-gray-200 leading-relaxed whitespace-pre-wrap">
              {structured.full_prompt}
            </p>
          </div>

          {/* Engagement Analysis */}
          <div className="bg-gradient-to-br from-green-500/10 to-lime-500/10 border border-green-500/30 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">📈</span>
              <h4 className="text-xl font-bold text-green-300">Engagement Optimization</h4>
            </div>
            <p className="text-gray-200 leading-relaxed">{structured.engagement_notes}</p>
          </div>
        </div>
      ) : (
        // Legacy format display
        <div className="bg-white/5 border border-white/10 rounded-xl p-6">
          <h4 className="text-lg font-bold text-gray-300 mb-3">Legacy Sora Script</h4>
          <p className="text-gray-200 leading-relaxed whitespace-pre-wrap">
            {result.sora_script}
          </p>
        </div>
      )}
    </div>
  );
}
