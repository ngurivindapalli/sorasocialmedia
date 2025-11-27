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
      {/* Stylized VH logo - VideoHook */}
      <path
        d="M8 8 L16 24 L24 8 M8 8 L8 24 M24 8 L24 24"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      {/* Decorative circle */}
      <circle
        cx="16"
        cy="16"
        r="14"
        stroke="currentColor"
        strokeWidth="1.5"
        fill="none"
        opacity="0.2"
      />
    </svg>
  )
}

export default Logo


