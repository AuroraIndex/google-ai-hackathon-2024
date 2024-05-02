import { Skeleton } from "@/components/ui/skeleton"

export default function LoadingDashboad() {
  return (
    <div className="flex items-center justify-center space-x-4 w-full h-full">
      <div className="grid grid-cols-4 gap-4">
        <Skeleton className="rounded-3xl h-[200px] w-[400px]" />
        <Skeleton className="rounded-3xl h-[200px] w-[400px]" />
        <Skeleton className="rounded-3xl h-[200px] w-[400px]" />
        <Skeleton className="rounded-3xl h-[200px] w-[400px]" />

        <Skeleton className="rounded-3xl h-[400px] w-[820px] col-span-2" />
        <Skeleton className="rounded-3xl h-[400px] w-[820px] col-span-2" />
        <Skeleton className="rounded-3xl h-[400px] w-[820px] col-span-2" />
        <Skeleton className="rounded-3xl h-[400px] w-[820px] col-span-2" />
      </div>
    <div className="absolute bottom-[50%] left-[50%] transform -translate-x-[50%] -translate-y-[50%]">
      <p className="text-3xl font-semibold text-gray-400">
      <span className="animate-pulse delay-[0s]">g</span>
      <span className="animate-pulse delay-[1s]">e</span>
      <span className="animate-pulse delay-[2s]">n</span>
      <span className="animate-pulse delay-[1s]">e</span>
      <span className="animate-pulse delay-[4s]">r</span>
      <span className="animate-pulse delay-[5s]">a</span>
      <span className="animate-pulse delay-[3s]">t</span>
      <span className="animate-pulse delay-[1s]">i</span>
      <span className="animate-pulse delay-[2s]">n</span>
      <span className="animate-pulse delay-[5s]">g</span>
      <span className="animate-pulse delay-[2s]">.</span>
      <span className="animate-pulse delay-[4s]">.</span>
      <span className="animate-pulse delay-[0s]">.</span>
      </p>
    </div>
    </div>
  )
}
