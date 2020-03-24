//
//  Reflection.swift
//

import Foundation

/// Return a useful name for an instance. In the case of a struct / class, this is the class name. In the case of an
/// enum, this is the case name i.e. `case event(when: Date)` would return the name `event`.
///
/// - parameter any: The object from which to extract the name
func asName(_ any: Any) -> String {
    let mirror = Mirror(reflecting: any)

    switch mirror.displayStyle {
    case .enum?:
        return mirror.children.first?.label ?? String(describing: any)
    default:
        return String(describing: mirror.subjectType)
    }
}

/// Returns the properties of the passed in object as a dictionary.
///
/// Properties which are `nil` are not returned in the response.
///
/// - parameter any: The object to inspect
/// - returns: A dictionary of properties and their values.
func asDictionary(_ any: Any) -> [String: Any]? {
    let mirror = Mirror(reflecting: any)

    switch mirror.displayStyle {
    case .enum?:
        guard let child = mirror.children.first else {
            return nil
        }

        // There's an interesting edge case here - rich enums with only one value don't store that value's name, just it's contents. We need to detect that and
        // deal with it here.

        // First, if this succeeds then we are all ok
        if let result = asDictionary(child.value) {
            return result
        }

        // Otherwise, the value on the child is the only value in the enum, so return it as a dictionary with the key .0 - just as for an anonymous rich enum
        // with multiple values - it's not ideal but there's not much more we can do.
        return [ ".0": child.value ]

    case .struct?, .tuple?, .class?:
        return mirror.children.reduce(nil) { dict, child in
            guard let name = child.label else { return dict }
            var dict = dict ?? [:]
            dict[name] = child.value
            return dict
        }

    default:
        return nil
    }
}
