//
//  LocalizableTests.swift
//

import Foundation
import XCTest

@testable import LocalizableGoogleSheets

// swiftlint:disable nesting

private enum RawRepresentableLocalizable: String, RawRepresentable, Localizable {
    static var localizationNamespace: String = ""

    case someStringToBeLocalized = "some.string.to.be.localized"
}

private enum ReplacableStringNameTest: Localizable {
    static var localizationNamespace: String = ""

    case replaceNameAndAge(name: String, age: Int)
}

private enum ReplacableSingleValueTest: Localizable {
    static var localizationNamespace: String = ""

    case one(value: String)

    static func localize(_ key: String) -> String {
        switch key {
        case "one": return "Just replace __value__"
        default: XCTFail("This test case doesn't (shouldn't) be asked to localize this key -> \(key)"); return ""
        }
    }
}

private enum ReplacableStringValueTest: Localizable {
    static var localizationNamespace: String = ""

    case noReplacements
    case someReplacements(name: String, age: Int)
    case oneReplacement(name: String, age: Int)


    static func localize(_ key: String) -> String {
        switch key {
        case "noReplacements": return "no.replacements"
        case "someReplacements": return "some.replacements name=__name__ age=__age__"
        case "oneReplacement": return "one.replacement name=__name__"
        default: XCTFail("This test case doesn't (shouldn't) be asked to localize this key -> \(key)"); return ""
        }
    }
}

enum TestPluralAndLocalizable: Localizable {
    static let localizationNamespace = "test.plural.and"

    case pluralReplacements(test: String)

    static var configuration: LocalizableConfiguration {
        return LocalizableConfiguration(tableName: nil, bundle: Bundle(for: LocalizationSpec.self))
    }
}


final class LocalizationSpec: XCTestCase {

    func testLocalizable_shouldUseRawRepresentable() {
        XCTAssertEqual(RawRepresentableLocalizable.someStringToBeLocalized.localizationKey, "some.string.to.be.localized")
    }

    func testLocalizable_shouldUseTypeNameToGetKey() {
        XCTAssertEqual(ReplacableStringNameTest.replaceNameAndAge(name: "Alice", age: 42).localizationKey, "replaceNameAndAge")
    }

    func testLocalizable_shouldBeOKWithNoReplacements() {
        XCTAssertEqual(ReplacableStringValueTest.noReplacements.localized, "no.replacements")
    }

    func testLocalizable_shouldReplaceSingleValueEnums() {
        XCTAssertEqual(ReplacableSingleValueTest.one(value: "x").localizationKey, "one")
        XCTAssertEqual(ReplacableSingleValueTest.one(value: "x").localized, "Just replace x")
    }

    func testLocalizable_shouldReplaceAllValues() {
        XCTAssertEqual(ReplacableStringValueTest.someReplacements(name: "Bob", age: 42).localized,
                       "some.replacements name=Bob age=42")
    }

    func testLocalizable_shouldApplyNamespaceInKey() {
        enum LocalizedNameTest: Localizable {
            static let localizationNamespace = "test.namespace"

            case example
        }

        XCTAssertEqual(LocalizedNameTest.example.localizationKey, "test.namespace.example")
    }

    func testLocalizable_shouldApplyNamespaceAndKeyWithRawRepresentable() {
        enum LocalizedNameTest: String, Localizable, RawRepresentable {
            static let localizationNamespace = "test.namespace"

            case example = "some.example"
        }

        XCTAssertEqual(LocalizedNameTest.example.localizationKey, "test.namespace.some.example")
    }

    func testLocalizable_shouldLocalizePlurals() {
        XCTAssertEqual(TestPluralAndLocalizable.pluralReplacements(test: "1").localized, "plural replacements = one")
        XCTAssertEqual(TestPluralAndLocalizable.pluralReplacements(test: "0").localized, "plural replacements = zero")
        XCTAssertEqual(TestPluralAndLocalizable.pluralReplacements(test: "2").localized, "plural replacements = other")
        XCTAssertEqual(TestPluralAndLocalizable.pluralReplacements(test: "5").localized, "plural replacements = other")
        XCTAssertEqual(TestPluralAndLocalizable.pluralReplacements(test: "230000").localized, "plural replacements = other")
        XCTAssertEqual(TestPluralAndLocalizable.pluralReplacements(test: "11").localized, "plural replacements = other")
    }

    func testLocalizable_shouldUseBundleToConvertToKeys() {
        /// There should be a string in the Localized.strings file for this test to pass
        ///
        /// The string in the strings file should be:
        ///
        /// ```
        /// "tests.example" = "A test example of a localized string";
        /// ```
        enum SimpleTest: Localizable {
            static let localizationNamespace = "tests"

            case example

            static var configuration: LocalizableConfiguration {
                return LocalizableConfiguration(tableName: nil, bundle: Bundle(for: LocalizationSpec.self))
            }
        }

        XCTAssertEqual(SimpleTest.example.localized, "A test example of a localized string")
    }

    func testLocalizable_shouldDealWithMissingKeys() {
        enum SimpleTest: Localizable {
            static var localizationNamespace: String = ""

            case notFound
        }

        XCTAssertEqual(SimpleTest.notFound.localized, "notFound")
    }
}
