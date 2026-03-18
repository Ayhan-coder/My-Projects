# PowerShell Script to Run CoreMark Benchmarks
# This script automates the process of running CoreMark with different optimization flags
# Make sure you have git and make (via MinGW or similar) installed first

# Change to the Lab 3 directory
Set-Location "c:\Users\gunde\Desktop\344Labs\344LAB3\coremark"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "CoreMark Automated Benchmark Script" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Function to run benchmark and extract results
function Run-Benchmark {
    param(
        [string]$OptFlag,
        [string]$Description,
        [int]$Runs = 5
    )
    
    Write-Host "Testing: $Description" -ForegroundColor Yellow
    Write-Host "Optimization Flag: $OptFlag" -ForegroundColor Yellow
    Write-Host ""
    
    # Clean previous build
    Write-Host "Cleaning previous build..." -ForegroundColor Gray
    make clean | Out-Null
    
    # Build with specified optimization
    Write-Host "Building with $OptFlag..." -ForegroundColor Gray
    if ($OptFlag -eq "default") {
        make
    } else {
        make XCFLAGS="$OptFlag"
    }
    
    Write-Host ""
    $results = @()
    
    # Run benchmark multiple times
    for ($i = 1; $i -le $Runs; $i++) {
        Write-Host "Run $i of $Runs..." -ForegroundColor Green
        
        # Run the benchmark
        if ($OptFlag -eq "default") {
            $output = make 2>&1 | Out-String
        } else {
            $output = make XCFLAGS="$OptFlag" 2>&1 | Out-String
        }
        
        # Extract Iterations/Sec from output
        if ($output -match "CoreMark 1\.0 : ([\d.]+)") {
            $iterationsPerSec = $matches[1]
            $results += [double]$iterationsPerSec
            Write-Host "  Result: $iterationsPerSec Iterations/Sec" -ForegroundColor Cyan
        } else {
            Write-Host "  Warning: Could not extract result from run $i" -ForegroundColor Red
        }
        
        Write-Host ""
    }
    
    # Calculate average
    if ($results.Count -gt 0) {
        $average = ($results | Measure-Object -Average).Average
        $min = ($results | Measure-Object -Minimum).Minimum
        $max = ($results | Measure-Object -Maximum).Maximum
        
        Write-Host "Summary for $Description ($OptFlag):" -ForegroundColor Magenta
        Write-Host "  Average: $average Iterations/Sec" -ForegroundColor Cyan
        Write-Host "  Min: $min" -ForegroundColor Gray
        Write-Host "  Max: $max" -ForegroundColor Gray
        Write-Host "  All values: $($results -join ', ')" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Return results object
    return @{
        OptFlag = $OptFlag
        Description = $Description
        Results = $results
        Average = $average
        Min = $min
        Max = $max
    }
}

# Array to store all benchmark results
$allResults = @()

# Get CPU information first
Write-Host "Getting CPU Information..." -ForegroundColor Yellow
$cpuInfo = Get-WmiObject Win32_Processor | Select-Object Name, MaxClockSpeed, NumberOfCores, NumberOfLogicalProcessors
Write-Host "CPU: $($cpuInfo.Name)" -ForegroundColor Cyan
Write-Host "Max Clock Speed: $($cpuInfo.MaxClockSpeed) MHz" -ForegroundColor Cyan
Write-Host "Cores: $($cpuInfo.NumberOfCores)" -ForegroundColor Cyan
Write-Host "Logical Processors: $($cpuInfo.NumberOfLogicalProcessors)" -ForegroundColor Cyan
Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Run benchmarks with different optimization flags
$allResults += Run-Benchmark -OptFlag "default" -Description "Default Build"
$allResults += Run-Benchmark -OptFlag "-O0" -Description "No Optimization"
$allResults += Run-Benchmark -OptFlag "-O1" -Description "Optimization Level 1"
$allResults += Run-Benchmark -OptFlag "-O2" -Description "Optimization Level 2"
$allResults += Run-Benchmark -OptFlag "-O3" -Description "Optimization Level 3"
$allResults += Run-Benchmark -OptFlag "-Ofast" -Description "Fast Optimization"

# Try -march=native (might not be supported on all compilers)
Write-Host "Attempting -march=native (this might fail on some systems)..." -ForegroundColor Yellow
try {
    $allResults += Run-Benchmark -OptFlag "-march=native" -Description "Native Architecture"
} catch {
    Write-Host "Note: -march=native is not supported on this compiler/system" -ForegroundColor Red
}

# Print summary table
Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "FINAL SUMMARY" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Optimization Flag    | Average Iterations/Sec | % Change from Default" -ForegroundColor Green
Write-Host "-------------------- | ---------------------- | ---------------------" -ForegroundColor Green

$defaultAvg = ($allResults | Where-Object { $_.OptFlag -eq "default" }).Average

foreach ($result in $allResults) {
    if ($result.Average) {
        $percentChange = if ($defaultAvg -gt 0) { 
            [math]::Round((($result.Average - $defaultAvg) / $defaultAvg) * 100, 2)
        } else { 
            0 
        }
        
        $optFlagFormatted = $result.OptFlag.PadRight(20)
        $avgFormatted = $result.Average.ToString("F2").PadLeft(22)
        $percentFormatted = "$percentChange%".PadLeft(21)
        
        Write-Host "$optFlagFormatted | $avgFormatted | $percentFormatted"
    }
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Benchmark Complete!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
