type CrmProMarkProps = {
  className?: string
  title?: string
}

export function CrmProMark({ className, title }: CrmProMarkProps) {
  const labelled = Boolean(title)

  return (
    <svg
      aria-hidden={labelled ? undefined : true}
      aria-label={title}
      className={className}
      fill="none"
      role={labelled ? 'img' : undefined}
      viewBox="0 0 48 48"
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect width="48" height="48" rx="14" fill="#18233F" />
      <path
        d="M14 32.5 24 15.5l10 17"
        stroke="#B9A6FF"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="3"
      />
      <path d="M14 32.5h20" stroke="#78D8C0" strokeLinecap="round" strokeWidth="3" />
      <circle cx="14" cy="32.5" r="4.5" fill="#78D8C0" />
      <circle cx="24" cy="15.5" r="4.5" fill="#A78BFA" />
      <circle cx="34" cy="32.5" r="4.5" fill="#5AB5F5" />
    </svg>
  )
}
