interface ErrorMessageProps {
  message: string
}

export function ErrorMessage({ message }: ErrorMessageProps) {
  return (
    <p role="alert" className="text-sm text-red-600 mt-1">
      {message}
    </p>
  )
}
