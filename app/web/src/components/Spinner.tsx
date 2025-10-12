export const LoadingScreen = () => {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
      <div
        style={{
          width: '3rem',
          height: '3rem',
          borderRadius: '999px',
          border: '4px solid rgba(37,99,235,0.2)',
          borderTopColor: '#2563eb',
          animation: 'spin 0.9s linear infinite',
        }}
      />
    </div>
  )
}

export const InlineSpinner = () => (
  <div
    style={{
      width: '1.5rem',
      height: '1.5rem',
      borderRadius: '999px',
      border: '3px solid rgba(37,99,235,0.2)',
      borderTopColor: '#2563eb',
      animation: 'spin 0.9s linear infinite',
    }}
  />
)
