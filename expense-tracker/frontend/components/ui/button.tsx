import * as React from "react"
import { cn } from "@/lib/utils"

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link'
  size?: 'default' | 'sm' | 'lg' | 'icon'
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'default', size = 'default', ...props }, ref) => {
    const baseStyles = "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"

    const variants = {
      default: "text-white hover:opacity-90 transition-opacity",
      destructive: "bg-red-500 text-white hover:bg-red-600",
      outline: "border bg-white hover:opacity-90 transition-opacity",
      secondary: "text-white hover:opacity-90 transition-opacity",
      ghost: "hover:opacity-80 transition-opacity",
      link: "underline-offset-4 hover:underline",
    }

    const variantStyles = {
      default: {
        backgroundColor: 'hsl(var(--button-primary))',
      },
      outline: {
        borderColor: 'hsl(var(--button-outline-border))',
        color: 'hsl(var(--heading-section))',
      },
      secondary: {
        backgroundColor: 'hsl(var(--button-secondary))',
        color: 'hsl(var(--heading-section))',
      },
      ghost: {
        color: 'hsl(var(--heading-section))',
      },
      link: {
        color: 'hsl(var(--heading-card))',
      },
    }

    const sizes = {
      default: "h-10 px-4 py-2",
      sm: "h-9 rounded-md px-3",
      lg: "h-11 rounded-md px-8",
      icon: "h-10 w-10",
    }

    return (
      <button
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        style={variant !== 'destructive' ? variantStyles[variant] : undefined}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button }
