import { useNavigate } from 'react-router-dom'

function Logo() {
  const navigate = useNavigate()

  const handleClick = (e) => {
    e.preventDefault()
    e.stopPropagation()
    // Navigate to dashboard instead of root
    navigate('/dashboard')
  }

  return (
    <svg
      width="32"
      height="32"
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="cursor-pointer"
      onClick={handleClick}
      style={{ cursor: 'pointer' }}
    >
      {/* Aigis Marketing Logo - Modern "A" with AI-inspired design */}
      {/* Main "A" shape */}
      <path
        d="M16 6 L10 26 L12 26 L13.5 20 L18.5 20 L20 26 L22 26 L16 6 Z"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      {/* Crossbar of "A" */}
      <line
        x1="13.5"
        y1="16"
        x2="18.5"
        y2="16"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
      {/* AI-inspired circuit pattern on the left */}
      <circle
        cx="8"
        cy="12"
        r="2"
        fill="currentColor"
        opacity="0.6"
      />
      <path
        d="M8 14 L8 18 M6 16 L10 16"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        opacity="0.6"
      />
      {/* AI-inspired circuit pattern on the right */}
      <circle
        cx="24"
        cy="12"
        r="2"
        fill="currentColor"
        opacity="0.6"
      />
      <path
        d="M24 14 L24 18 M22 16 L26 16"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        opacity="0.6"
      />
    </svg>
  )
}

export default Logo
