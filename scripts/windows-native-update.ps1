# Real Windows UI Automation against the already-installed native Qt baseline.
param([Parameter(Mandatory=$true)][string]$Exe)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$evidence=Join-Path $pwd 'work/native-evidence/native-update-ui'
$null=New-Item -ItemType Directory -Path $evidence -Force
$script:receipts=@()
function Find-Control($Root,[string]$Name,$Type,[int]$Timeout=40) {
  $condition=New-Object System.Windows.Automation.AndCondition -ArgumentList @(
    (New-Object System.Windows.Automation.PropertyCondition -ArgumentList @([System.Windows.Automation.AutomationElement]::NameProperty,$Name)),
    (New-Object System.Windows.Automation.PropertyCondition -ArgumentList @([System.Windows.Automation.AutomationElement]::ControlTypeProperty,$Type))
  )
  $deadline=(Get-Date).AddSeconds($Timeout)
  do {
    try{$found=$Root.FindFirst([System.Windows.Automation.TreeScope]::Descendants,$condition);if($found){return $found}}catch{}
    Start-Sleep -Milliseconds 250
  }while((Get-Date) -lt $deadline)
  throw ('Native UI control not found: '+$Name)
}
function Invoke-Control($Element,[string]$Name){
  $deadline=(Get-Date).AddSeconds(30)
  do {if($Element.Current.IsEnabled){break};Start-Sleep -Milliseconds 250}while((Get-Date) -lt $deadline)
  if(-not $Element.Current.IsEnabled){throw ('Native UI control disabled: '+$Name)}
  $pattern=$Element.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
  $pattern.Invoke()
  $script:receipts+=@{control=$Name;action='InvokePattern';at=(Get-Date).ToUniversalTime().ToString('o')}
}
try {
  $null=Start-Process -FilePath $Exe -PassThru
  $desktop=[System.Windows.Automation.AutomationElement]::RootElement
  $window=Find-Control $desktop 'WinOptimizer Aion' ([System.Windows.Automation.ControlType]::Window)
  $script:baselineProcessId=$window.Current.ProcessId
  Invoke-Control (Find-Control $window 'Settings' ([System.Windows.Automation.ControlType]::Button)) 'Settings'
  $combo=Find-Control $window 'Settings' ([System.Windows.Automation.ControlType]::ComboBox)
  $combo.GetCurrentPattern([System.Windows.Automation.ExpandCollapsePattern]::Pattern).Expand()
  # Qt popup windows can be siblings of the main window in the accessibility tree.
  $item=Find-Control $desktop 'Updates' ([System.Windows.Automation.ControlType]::ListItem)
  $item.GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern).Select()
  $script:receipts+=@{control='Updates';action='SelectionItemPattern'}
  Invoke-Control (Find-Control $window 'Check for updates' ([System.Windows.Automation.ControlType]::Button)) 'Check for updates'
  $install=Find-Control $window 'Update and restart' ([System.Windows.Automation.ControlType]::Button) 120
  Invoke-Control $install 'Update and restart'
  # User confirmation is exercised rather than calling the updater service directly.
  Invoke-Control (Find-Control $desktop 'OK' ([System.Windows.Automation.ControlType]::Button)) 'OK'
  @{baselineProcessId=$script:baselineProcessId;controls=$script:receipts}|ConvertTo-Json -Depth 6|Set-Content (Join-Path $evidence 'invoked-controls.json') -Encoding UTF8
  Write-Host 'Native Settings -> Updates -> authenticated update invoked through Windows UI Automation'
}catch{
  @{baselineProcessId=$script:baselineProcessId;controls=$script:receipts}|ConvertTo-Json -Depth 6|Set-Content (Join-Path $evidence 'invoked-controls.json') -Encoding UTF8
  try {
    $nodes=[System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
    $dump=@();foreach($node in $nodes){try{if($node.Current.Name){$dump+=@{name=$node.Current.Name;type=$node.Current.ControlType.ProgrammaticName;id=$node.Current.AutomationId;process=$node.Current.ProcessId}}}catch{}}
    $dump|ConvertTo-Json -Depth 4|Set-Content (Join-Path $evidence 'accessible-controls.json') -Encoding UTF8
  }catch{}
  throw
}
