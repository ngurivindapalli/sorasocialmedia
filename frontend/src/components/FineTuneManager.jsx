import { useState } from 'react';
import axios from 'axios';

export default function FineTuneManager() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);

  const loadJobs = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/api/finetune/list');
      setJobs(response.data.fine_tune_jobs);
    } catch (error) {
      console.error('Error loading fine-tune jobs:', error);
      alert('Error loading jobs: ' + (error.response?.data?.detail || error.message));
    }
    setLoading(false);
  };

  const createFineTune = async () => {
    // Example training data - in production, you'd collect this from analyzed videos
    const trainingData = {
      examples: [
        {
          transcription: "Welcome to our AI channel. Today we're exploring the future of artificial intelligence and how it's transforming video creation.",
          metadata: { views: 50000, likes: 2500 },
          ideal_sora_prompt: "A sleek, modern studio setting with soft purple and blue lighting. Camera slowly pushes in on a tech presenter standing confidently. Holographic AI visualizations float around them. Professional, cinematic grade with shallow depth of field. 16:9 aspect ratio, 30 seconds."
        },
        {
          transcription: "Check out this amazing sunset timelapse captured from our rooftop.",
          metadata: { views: 100000, likes: 5000 },
          ideal_sora_prompt: "Golden hour timelapse of a vibrant sunset over a city skyline. Colors transition from warm orange to deep purple. Clouds move rapidly across the frame. Camera locked on tripod. Cinematic color grading with enhanced saturation. 16:9, smooth motion blur."
        }
      ]
    };

    setCreating(true);
    try {
      const response = await axios.post('http://localhost:8000/api/finetune/create', trainingData);
      alert(`Fine-tune job created! ID: ${response.data.fine_tune_id}\n\nStatus: ${response.data.status}`);
      loadJobs();
    } catch (error) {
      console.error('Error creating fine-tune:', error);
      alert('Error: ' + (error.response?.data?.detail || error.message));
    }
    setCreating(false);
  };

  return (
    <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
      <h2 className="text-2xl font-bold text-white mb-4">🎯 Fine-Tuning Manager</h2>
      <p className="text-white/70 mb-4">
        Create custom GPT models trained on your best Sora prompts for even better results.
      </p>

      <div className="flex gap-4 mb-6">
        <button
          onClick={createFineTune}
          disabled={creating}
          className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-xl hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 transition-all"
        >
          {creating ? 'Creating...' : 'Create Fine-Tune Job (Demo)'}
        </button>
        <button
          onClick={loadJobs}
          disabled={loading}
          className="px-6 py-3 bg-white/10 text-white font-semibold rounded-xl hover:bg-white/20 disabled:opacity-50 transition-all"
        >
          {loading ? 'Loading...' : 'Refresh Jobs'}
        </button>
      </div>

      {jobs.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-white">Your Fine-Tune Jobs:</h3>
          {jobs.map((job) => (
            <div key={job.id} className="bg-white/5 rounded-lg p-4 border border-white/10">
              <div className="flex justify-between items-start mb-2">
                <span className="text-white font-mono text-sm">{job.id}</span>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                  job.status === 'succeeded' ? 'bg-green-500/20 text-green-300' :
                  job.status === 'running' ? 'bg-blue-500/20 text-blue-300' :
                  job.status === 'failed' ? 'bg-red-500/20 text-red-300' :
                  'bg-yellow-500/20 text-yellow-300'
                }`}>
                  {job.status}
                </span>
              </div>
              <p className="text-white/60 text-sm">Base Model: {job.model}</p>
              {job.fine_tuned_model && (
                <div className="mt-2 p-2 bg-purple-500/10 rounded border border-purple-500/20">
                  <p className="text-purple-300 text-xs font-semibold mb-1">✅ Ready to use!</p>
                  <p className="text-white/80 text-xs font-mono break-all">{job.fine_tuned_model}</p>
                  <p className="text-white/60 text-xs mt-2">
                    Add to .env: OPENAI_FINE_TUNED_MODEL={job.fine_tuned_model}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="mt-6 p-4 bg-blue-500/10 rounded-lg border border-blue-500/20">
        <p className="text-blue-200 text-sm">
          <strong>💡 Tip:</strong> Fine-tuning trains a custom model on your examples. 
          Costs ~$0.80 per 1K training tokens. Once complete, add the model ID to your .env file 
          and restart the backend to use it automatically!
        </p>
      </div>
    </div>
  );
}
