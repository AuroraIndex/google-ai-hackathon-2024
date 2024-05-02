import { Skeleton } from "@/components/ui/skeleton"

interface LoadingDashboardProps {
  word?: string
}

export default function LoadingDashboad({word = "generating..."}: LoadingDashboardProps) {
  return (
    <div className="flex items-center justify-center space-x-4 w-full h-full">
      <div className="grid grid-cols-2 gap-4">
        <Skeleton className="rounded-3xl h-[200px] w-[400px]" />
        <Skeleton className="rounded-3xl h-[200px] w-[400px]" />

        <Skeleton className="rounded-3xl h-[400px] w-[820px] col-span-2" />
        <Skeleton className="rounded-3xl h-[400px] w-[820px] col-span-2" />
      </div>
    <div className="absolute bottom-[50%] left-[50%] transform -translate-x-[50%] -translate-y-[50%]">
      <p className="text-3xl font-semibold text-gray-400">
      {Array.from(word).map((char, index) => (
            <span
              key={index}
              className="inline-block animate-pulse"
              style={{
                animationDelay: `${Math.random() * 1}s`,
                animationDuration: `${Math.random() * 1 + 1}s`,
                opacity: Math.random(),
                // transform: `scale(${Math.random() * 0.5 + 1})`,
              }}>
              {char}
            </span>
          ))}

      </p>
    </div>
    </div>
  )
}
