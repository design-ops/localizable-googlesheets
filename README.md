# LocalizableGoogleSheets
Tool for managing iOS translations from Google Sheets

## Prerequisites

1. Install Docker

1. Create a Google Sheet with a worksheet called "Translations" with the following structure

	| key | en | pt |
	| --- | --- | --- |
	| key.in.dot.notation | text in english | text in portuguese
	
	* you may add `-` and any comments or notes in the header, eg `en - English` or `key - developer key, do not edit if you are not a developer`
	* likewise if you would like to add other columns, add a `-` at the start of the header and they will be ignored.
1. If you wish to support plurals, then add a second worksheet with the following structure

    | VARIABLE | EXAMPLE | LANG | ZERO | ONE | TWO | FEW | MANY | OTHER |
	| --- | --- | --- | --- | --- | --- | --- | --- | --- |
	| ${ice_cream_toppings} | You have ${ice_cream_toppings} on your ice cream | en | no toppings | one topping | two toppings | few toppings | many toppings | ${ice_cream_toppings} toppings |
    | ${ice_cream_toppings} | You have ${ice_cream_toppings} on your ice cream | pt | zero toppings | um topping | dois toppings | poucos toppings | muitos toppings | ${ice_cream_toppings} toppings |
	
	* Please refer to the [Apple Localisation Documentation](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPInternational/StringsdictFileFormat/StringsdictFileFormat.html) and [Unicode plural rules](http://www.unicode.org/cldr/charts/latest/supplemental/language_plural_rules.html) for more information about how and when to use the zero, one, two, few, many and other columns (only other is mandatory).


1. Activate the Google Sheets API
    - Go to the [Google APIs Dashboard](https://console.developers.google.com/apis/dashboard)
    - Select an existing project or create a new one.
    - Tap **Enable APIs and Services** and then find and enable the Google Sheets API [this link may take you there depending on a number of factors](https://console.developers.google.com/apis/library/sheets.googleapis.com).
    - From the dashboard select **Credentials** and then create new **OAuth Client ID** credentials of type **Other**  and download the JSON file.
    - Once you've created the credentials, you have to set up the OAuth consent screen by selecting the support email in the consent screen and clicking save.
    - Save the file somewhere safe and use it in the step below.

1. Have the id of the Google Sheet handy
  - You can find this in the url of your google doc, i.e. for the example url is `https://docs.google.com/spreadsheets/d/1RT1c2zcTMk_dR3qYVq9GKXJthczACCJbqulVqbQrFxI/` so the id would be `1RT1c2zcTMk_dR3qYVq9GKXJthczACCJbqulVqbQrFxI`.

## Quick Start

### Build the docker container

`bin/setup.sh`

### Run the localisation bash script

`bin/localisation.sh -s id_of_the_sheet -p path_to_xcode_project -c path_to_credentials_json`

This will generate the code and copy the files into the XCode project. 

### First Run

* Before you run the script:
	* Enable localisation in the xcode project (aka create `Localizable.strings` and `Localizable.stringsdict` files)

* First time you run the script you'll need to:
	* copy the enum (`.swift`) files into the repo


### Notes

- A key `key.in.dot.notation` will generate an enum named `KeyInDotLocalizable` with a value `notation`

- To localize a string with dynamic values in it, surround the dynamic value with `<>` e.g. `This is a <dynamicValue>` will product a localizable key with a named parameter called `dynamicValue` that you can use in your app.

- You can add the same key for multiple values, and update the `plural` row with either `zero`, `one`, `two`, `few`, `many` or `other` - which are the plurals that Swift support - to generate add it to `Localizable.stringsdict` instead. Caveat: values here may only have one dynamic value, multiple plurals for the same key are not supported. 

### Preventing manual editing of the generated files

The script generates a `.checksum.localizablegooglesheets` file - which contains an sha1 checksum for each `Localizable.strings` file - and a `.validate_checksum.sh` that validates the checksums contained in the `.checksum.localizablegooglesheets` file against a `shasum` of the current Localizable.strings files. 
Both of these files will be copied to the provided XCode project path root by the script.

**NB:** If you move both these files into another directory, the script will overwrite them instead of copying them to the root folder; Be sure to update the `Run Script` path if you do this.  

If any of the Localizable.strings files have been manually edited, the validator will fail the build

To use this validation, add a new `Build Phase - Run Script` with the following line: 
```bash
"${PROJECT_DIR}/.validate_checksum.sh"
```

And that's it!


### SYNOPSIS


```
localisation - generate swift enums, `localizable.strings`, `localizable.stringsdict` files, and a CSV snapshot from a Google Sheet


    ./bin/localisation -s <sheet_id> -p <project_dir> -c <google_credentials_json>

MANDATORY ARGUMENTS

    -s <id> id of google sheet to process
    -p <path> path to project dir to automatically update files
    -c <path> path to the google cloud credentials

OPTIONAL ARGUMENTS

  -b set this flag to bypass the csv generation and use the CSV that's in the specified dir
  -o <path> path to folder to generate code into (defaults to output folder in project)
  -h  display this help text
```

## Example

To run the example project, clone the repo, and run `pod install` from the Example directory first.

## Requirements

## Installation

LocalizableSheets is available through [CocoaPods](https://cocoapods.org). To install
it, simply add the following line to your Podfile:

```ruby
pod 'LocalizableGoogleSheets'
```


## How it works

The localisation script is wrapped in a handy dockerized bash script for ease of usage but it's built in Python 3.7

It begins by generating a CSV snapshot from the Google Sheet, which is then copied to the project dir. If the `-b` option is specified, the generation is skipped and the script searches for the CSV in the project dir.

An enum with the keys is generated and copied to the respective directory in each project. This works by searching where the previous enum is and replacing it. 

One `localizable.strings` file is generated **per localization** and then copied to the project dir, replacing the existing ones. 
Same thing for `Localizable.stringsdict` files.

If there are no files to replace, the copy will *NOT* work. This means you will have to copy the files manually on the first run. You also need to add the relevant files to the project.
