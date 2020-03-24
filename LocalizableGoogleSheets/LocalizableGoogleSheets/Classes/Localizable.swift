//
//  Localizable.swift
//

import Foundation

/// Implement `Localizable` to get localized text, including replacements as part of rich enum keys.
///
/// i.e.
/// ```
/// enum ExampleStrings: Localizable {
///     static let localizationNamespace = "localizable.example"
///
///     case welcome(name: String)
/// }
/// ```
///
/// Get the localised string by calling `localized` on an instance of that enum i.e.
///
/// ```
/// ExampleStrings.welcome(name: "Paula Bean").localized
/// ```
///
/// This will fetch the localized string from the main bundle for the key `"localizable.example.welcome"`
/// and replace any instances of `"<name>"` with `"Paula Bean"`.
public protocol Localizable {

    /// This is prepended to every `localizationKey` provided by this type. Returning `""` will not prepend anything.
    static var localizationNamespace: String { get }

    /// This key is passed into the localize method (by default NSLocalizedString) to produce a value based on the current
    /// locale. Default implementations of this will automatically prepend the namespace - if this is overridden, it's
    /// the responsibility of the new method to apply (or not) the namespace.
    var localizationKey: String { get }

    /// Implementations of `Localizable` can specify _how_ they want to convert the key to the localized string. The default implementation will
    /// just call out to `NSLocalizedString(_:comment:)`.
    ///
    /// This method should not attempt to do any substitution, this is just fetching the raw localized string for a given key.
    ///
    /// - warning: You almost certainly don't want to set this to anything other than the default.
    static func localize(_ key: String) -> String

    /// The localized text for this `Localizable`, after any needed substitutions have been made.
    var localized: String { get }

    static var configuration: LocalizableConfiguration { get }
}

public struct LocalizableConfiguration {
    let tableName: String?
    let bundle: Bundle

    init(tableName: String? = nil, bundle: Bundle = .main) {
        self.tableName = tableName
        self.bundle = bundle
    }
}

public extension Localizable {
    static var configuration: LocalizableConfiguration { return LocalizableConfiguration() }
}

public extension Localizable {

    /// Default implementation of `localizationKey` will return this type's name.
    ///
    /// Implementing `RawRepresentable` will allow an easy way to provide custom `localizationKey` values, at the cost of
    /// prohibiting rich enums (i.e. substitution).
    var localizationKey: String { return asName(self).prependingNamespace(Self.localizationNamespace) }
}

public extension Localizable where Self: RawRepresentable, Self.RawValue == String {

    /// Implementations of `Localizable` which are RawRepresentable as a String will return their raw value as the
    /// localisation key.
    var localizationKey: String { return self.rawValue.prependingNamespace(Self.localizationNamespace) }
}

public extension Localizable {

    /// Default implementation of `localize` just calls out to `NSLocalizedString(_:comment:)`.
    ///
    /// This implementation also warns about missing keys in DEBUG builds.
    ///
    /// - parameter key: The key to localize.
    /// - returns: A localized string for the given key (or if one cannot be found, the original key is returned).
    static func localize(_ key: String) -> String {
        return seamlessLocalizedString(key, tableName: self.configuration.tableName, bundle: self.configuration.bundle, comment: "")
    }

    /// The default implementation of localized will fetch the localized string from the strings file and replace
    /// any substitutions before returning the localized string back to the caller.
    var localized: String {
        // Get the translated value (use the super-protocol's implementation of this)
        let localized = Self.localize(self.localizationKey)

        // Get a list of all the possible replacements we need to make in the string. Use this to validate they have been
        // replaced after the `reduce`
        var replacements = Set(localized.replacements)

        // Get the dictionary of values to replace (i.e. a rich enum's values, or a struct's fields)
        let localizations = asDictionary(self) ?? [:]

        // Handling plurals:
        if replacements.isEmpty {
            let args = self.orderedElements(localizations, forFormat: localized)
            let pluralsReplaced = String(format: localized, arguments: args)

            let replacedString = try! self.replaceInstances(of: "__(\\w*)?__", in: pluralsReplaced, with: "%@")
            // Every plural is an Int, so we remove them from the args since they've already been replaced
            let cleanedArgs = args.filter{ $0 is String }

            // Take the replaced string and re-format it with the cleaned arguments
            return String(format: replacedString, arguments: cleanedArgs)
        }
        // End of handling plurals

        // There's an edge case - if there is only one localisation and the dictionary contains one key `".0"` then
        // that's what we should use (Swift doesn't store rich enum names if there is only one value).
        // Just do the single replacement and return
        if replacements.count == 1,
            let replacement = replacements.first,
            localizations.keys.count == 1,
            let value = localizations[".0"] {

            return localized.replacingOccurrences(of: "__" + replacement + "__", with: String(describing: value))
        }

        // Replace instances of them surrounded by __…__ in the localized string.
        let replaced = localizations.reduce(localized) { str, keyVal in
            replacements.remove(keyVal.key)
            return str.replacingOccurrences(of: "__" + keyVal.key + "__",
                                            with: String(describing: keyVal.value))
        }

        // Validate that all the replacements have been made. Sigh, regular expressions :|
        replacements.forEach { printMissingReplacementWarning(for: localized, replacement: $0) }

        return replaced
    }

    private func replaceInstances(of needle: String, in haystack: String, with replacement: String) throws -> String {
        let range = NSRange(location: 0, length: haystack.utf16.count)
        let regex = try NSRegularExpression(pattern: needle)
        return regex.stringByReplacingMatches(in: haystack, options: [], range: range, withTemplate: replacement)
    }

    /// We need to order the elements in the localizations dict so they conform to the format.
    /// This is because in each language there may be ordered differently.
    private func orderedElements(_ elements: [String: Any], forFormat format: String) -> [CVarArg] {
        let regex = try! NSRegularExpression(pattern: "__.+?__")

        let range = NSRange(location: 0, length: format.utf16.count)
        let matches = regex.matches(in: format, options: [], range: range)

        let orderedElements = matches.map { match -> String in
            let el = String(format[Range(match.range, in: format)!])
            // Convert to camelCase
            return el.replacingOccurrences(of: "__", with: "")
                .split(separator: "_")
                .enumerated()  // get indices
                .map { $0.offset > 0 ? $0.element.capitalized : $0.element.lowercased() } // added lowercasing
                .joined()
        }

        return orderedElements.compactMap { elements[$0] as? String }
                              .map { string -> CVarArg in return Int(string) ?? string }

    }
}

fileprivate extension String {

    /// Prepends the passed in string and a `"."` to the reciever, and returns the new String
    ///
    /// - parameter value: The string to prepend. If this string is empty, then the reciever is returned unchanged.
    func prependingNamespace(_ value: String) -> String {
        guard !value.isEmpty else { return self }

        return value + "." + self
    }

    static let replacementRegularExpression: NSRegularExpression = {
        do {
            return try NSRegularExpression(pattern: "^[^%#@]*__(\\w*)?__[^@]*$", options: [ ])
        } catch {
            fatalError("Failed to create regular expression: \(error)")
        }
    }()

    /// Returns a list of all the replacement placeholder values in a string. Essentially, everything contained between
    /// `__` and `__` will be returned.
    var replacements: [String] {
        let string = self as NSString
        return String.replacementRegularExpression
            .matches(in: self, options: [ ], range: NSRange(location: 0, length: string.length))
            .map { string.substring(with: $0.range(at: 1)) }
    }
}

/// Platform wrapper around `NSLocalizedString`.
func seamlessLocalizedString(_ key: String, tableName: String? = nil, bundle: Bundle = .main, value: String = "", comment: String) -> String {
    let localized = NSLocalizedString(key, tableName: tableName, bundle: bundle, value: value, comment: comment)

    // If the returned value is the same as the key, then we can assume that the key wasn't found in the strings file.
    if key == localized {
        printMissingKeyWarning(for: key)
    }

    return localized
}

// MARK: - Debug warning methods

#if DEBUG

/// Stores a list of keys which have already been warned - used to prevent multiple warnings for missing localizable keys.
private var missingKeyWarnings: [String] = []
private var missingReplacementWarnings: [String] = []

#endif /* DEBUG */

/// Outputs a warning for a missing localization key. It will only output a warning once per key.
///
/// - note: This method is just an empty stub in release builds.
///
/// - parameter key: The key for which to output a warning.
private func printMissingKeyWarning(for key: String) {
    #if DEBUG

    guard !missingKeyWarnings.contains(key) else { return }

    missingKeyWarnings.append(key)

    print("⚠️ l10n: Missing localized value for key '\(key)'")

    #endif /* DEBUG */
}

/// Outputs a warnings for a missing key in a localized string. It will only output a warning once per key per missing replacement.
///
/// For example, using `case test(firstName: String)` to localize `"Ms <firstName> <lastName>"` would output a warning for `lastName`.
///
/// - note: This method is just an empty stub in release builds
///
/// - parameter key: The key for which to output a warning
/// - parameter replacement: The replacement which was missing
private func printMissingReplacementWarning(for key: String, replacement: String) {
    #if DEBUG

    let key = key.replacingOccurrences(of: "\n", with: "\\n")

    let warning = "'\(key)' is missing replacement for key '\(replacement)'"

    guard !missingReplacementWarnings.contains(warning) else { return }

    missingReplacementWarnings.append(warning)

    print("⚠️ l10n:", warning)

    #endif /* DEBUG */
}
