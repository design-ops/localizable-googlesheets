//
//  ViewController.swift
//  LocalizableSheets
//

import UIKit

final class ViewController: UIViewController {

    @IBOutlet private weak var saucesStepper: UIStepper!
    @IBOutlet private weak var toppingsStepper: UIStepper!
    @IBOutlet private weak var numberOfSaucesLabel: UILabel!
    @IBOutlet private weak var numberOfToppingsLabel: UILabel!
    @IBOutlet private weak var saucesAndToppingsLabel: UILabel!

    @IBOutlet private weak var noArgumentsLabel: UILabel!
    @IBOutlet private weak var oneArgumentLabel: UILabel!
    @IBOutlet private weak var twoArgumentsLabel: UILabel!
    @IBOutlet private weak var pluralLabel: UILabel!
    @IBOutlet private weak var mixedLabel: UILabel!

    static private let formatter: NumberFormatter = {
        let formatter = NumberFormatter()
        formatter.numberStyle = .none
        return formatter
    }()

    override func viewDidLoad() {
        super.viewDidLoad()
        self.saucesStepper.minimumValue = 0
        self.toppingsStepper.minimumValue = 0
        self.saucesStepper.value = 0
        self.toppingsStepper.value = 0

        self.saucesStepper.addTarget(self, action: #selector(saucesOrToppingsStepperChanged), for: .valueChanged)
        self.toppingsStepper.addTarget(self, action: #selector(saucesOrToppingsStepperChanged), for: .valueChanged)

        self.noArgumentsLabel.text = SimpleLocalizable.example.localized
        self.pluralLabel.text = PluralsLocalizable.plural(x: "1").localized
        self.oneArgumentLabel.text = DynamicArgumentsLocalizable.one(arg: "arg1").localized
        self.twoArgumentsLabel.text = DynamicArgumentsLocalizable.two(arg1: "arrrrrg1", arg2: "arrrrrg3").localized
        // TODO: Allow mix-and-match
        self.mixedLabel.text = PluralsLocalizable.pluralAndSingular(myValue: "hello!", y: "3", z: "this is a test").localized
    }

    @objc private func saucesOrToppingsStepperChanged() {
        let numberOfSauces = NSNumber(value: self.saucesStepper.value)
        let numberOfToppings = NSNumber(value: self.toppingsStepper.value)
        let newSaucesText = ViewController.formatter.string(from: numberOfSauces)
        let newToppingsText = ViewController.formatter.string(from: numberOfToppings)
        self.numberOfSaucesLabel.text = newSaucesText
        self.numberOfToppingsLabel.text = newToppingsText
        self.saucesAndToppingsLabel.text = IcecreamLocalizable.saucesAndToppingsTitle(iceCreamToppings: newToppingsText ?? "0", iceCreamSauces: newSaucesText ?? "0").localized
    }
}

