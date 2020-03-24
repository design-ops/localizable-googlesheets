
Pod::Spec.new do |s|
  s.name             = 'LocalizableGoogleSheets'
  s.version          = '1.0.0'
  s.summary          = 'Tool for transforming Google Spreadsheets of translations into iOS ready files'
  s.description      = <<-DESC
Provides a `Localizable` protocol to enable easy transfer from enums to associated localisation strings/stringsdict files.
Handles variable substitution and plurals.
Also includes a standalone convertor (written in Python, running in Docker) which will generate the necessary localisation/translation
strings/stringsdict files and the associated Localizable conforming enums.
                       DESC
  s.homepage         = 'https://github.com/design-ops/localizable-googlesheets'
  s.license          = { :type => 'MIT', :file => 'LICENSE' }
  s.authors          = 'nmpsilva', 'deanWomborne', 'kerrmarin', 'atomoil'
  s.source           = { :git => 'https://github.com/design-ops/localizable-googlesheets.git', :tag => "v#{s.version}" }
  
  s.swift_version = '5.0'
  s.ios.deployment_target = '8.0'
  
  s.source_files = 'LocalizableGoogleSheets/LocalizableGoogleSheets/Classes/**/*'
  
  s.test_spec 'Tests' do |test_spec|
    test_spec.source_files = 'LocalizableGoogleSheets/LocalizableGoogleSheets/Tests/*'
    test_spec.resources = 'LocalizableGoogleSheets/LocalizableGoogleSheets/Tests/Resources/*'
  end  
  
  s.frameworks = 'Foundation'
  
end
