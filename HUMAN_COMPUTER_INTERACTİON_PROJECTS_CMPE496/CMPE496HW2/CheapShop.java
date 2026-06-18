import javax.swing.*;
import javax.swing.border.TitledBorder;
import java.awt.*;
import java.awt.event.*;
import java.util.ArrayList;

/**
 * @author Ali Ayhan Gunder - 2021400219
 * @date 2025-14-07
 * CheapShop is a simple catalog store application using Swing for GUI.
 * It allows users to enter purchaser information and catalog items, then generates an invoice.
 */
public class CheapShop extends JFrame {
    /** Purchaser name field */
    JTextField nameField;
    /** Purchaser phone field */
    JTextField phoneField;
    /** Purchaser postal code field */
    JTextField postalField;
    /** Purchaser province field */
    JTextField provinceField;
    /** Purchaser city field */
    JTextField cityField;
    /** Purchaser address field */
    JTextField addressField;
    /** Date field */
    JTextField dateField;
    /** Credit card field */
    JTextField ccField;
    /** Validation ID field (optional) */
    JTextField validationIdField;
    /** Catalog item number field */
    JTextField itemNumberField;
    /** Catalog item cost field */
    JTextField costField;
    /** Catalog item total field (read-only) */
    JTextField totalField;
    /** Balance owing field (read-only) */
    JTextField balanceField;
    /** Catalog item quantity spinner */
    JSpinner quantitySpinner;
    /** Button to add next catalog item */
    JButton nextItemBtn;
    /** Button to trigger invoice */
    JButton triggerInvoiceBtn;
    /** Purchaser info panel */
    JPanel purchaserPanel;
    /** Catalog item panel */
    JPanel catalogPanel;
    /** Button panel */
    JPanel btnPanel;
    /** Center panel */
    JPanel centerPanel;
    /** List of catalog items */
    private ArrayList<CatalogItem> items = new ArrayList<>();
    /** Current balance owing */
    private double balanceOwing = 0.0;
    /** Whether purchaser info has been entered */
    private boolean purchaserInfoEntered = false;
    /** Purchaser info object */
    private PurchaserInfo purchaserInfo = null;

    /**
     * Constructs the CheapShop main window and initializes components.
     */
    public CheapShop() {
        setTitle("Cheap Shop Catalog Store");
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setResizable(false);
        initComponents();
        showPurchaserScreen();
        pack();
        setLocationRelativeTo(null);
        setVisible(true);
    }

    /**
     * Initializes all Swing components and sets up listeners and keyboard shortcuts.
     */
    private void initComponents() {
        // Purchaser fields
        nameField = new JTextField(12);
        phoneField = new JTextField(10);
        postalField = new JTextField(8);
        provinceField = new JTextField(6);
        cityField = new JTextField(10);
        addressField = new JTextField(30);
        dateField = new JTextField(10);
        ccField = new JTextField(14);
        validationIdField = new JTextField(8);
        // Catalog item fields
        itemNumberField = new JTextField(6);
        quantitySpinner = new JSpinner(new SpinnerNumberModel(1, 1, 999, 1));
        costField = new JTextField(6);
        totalField = new JTextField(8);
        totalField.setEditable(false);
        balanceField = new JTextField(8);
        balanceField.setEditable(false);
        // Buttons (consistent labels)
        nextItemBtn = new JButton("Next Catalog Item (F5)");
        triggerInvoiceBtn = new JButton("Trigger Invoice (F8)");
        // Mnemonics for accessibility
        nextItemBtn.setMnemonic(KeyEvent.VK_N); // Alt+N
        triggerInvoiceBtn.setMnemonic(KeyEvent.VK_T); // Alt+T
        // Listeners
        nextItemBtn.addActionListener(e -> addCatalogItem());
        triggerInvoiceBtn.addActionListener(e -> triggerInvoice());
        costField.addKeyListener(new KeyAdapter() {
            public void keyReleased(KeyEvent e) { updateTotalField(); }
        });
        quantitySpinner.addChangeListener(e -> updateTotalField());
        // Keyboard shortcuts (F5 for Next, F8 for Invoice)
        InputMap inputMap = getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW);
        ActionMap actionMap = getRootPane().getActionMap();
        inputMap.put(KeyStroke.getKeyStroke(KeyEvent.VK_F5, 0), "nextItem");
        actionMap.put("nextItem", new AbstractAction() {
            public void actionPerformed(ActionEvent e) { nextItemBtn.doClick(); }
        });
        inputMap.put(KeyStroke.getKeyStroke(KeyEvent.VK_F8, 0), "triggerInvoice");
        actionMap.put("triggerInvoice", new AbstractAction() {
            public void actionPerformed(ActionEvent e) { triggerInvoiceBtn.doClick(); }
        });
    }

    /**
     * Shows the purchaser information entry screen (Screen 1).
     */
    private void showPurchaserScreen() {
        getContentPane().removeAll();
        setLayout(new BorderLayout(8, 8));
        purchaserPanel = new JPanel(new GridBagLayout());
        purchaserPanel.setBorder(BorderFactory.createTitledBorder(BorderFactory.createEtchedBorder(), "Purchaser", TitledBorder.LEFT, TitledBorder.TOP, null, Color.BLACK));
        GridBagConstraints c = new GridBagConstraints();
        c.insets = new Insets(2, 4, 2, 4);
        c.fill = GridBagConstraints.HORIZONTAL;
        // Name
        c.gridx = 0; c.gridy = 0;
        purchaserPanel.add(new JLabel("Name:"), c);
        c.gridx = 1;
        purchaserPanel.add(nameField, c);
        c.gridx = 2;
        purchaserPanel.add(new JLabel("Phone:"), c);
        c.gridx = 3;
        purchaserPanel.add(phoneField, c);
        c.gridx = 0; c.gridy++;
        purchaserPanel.add(new JLabel("Postal Code:"), c);
        c.gridx = 1;
        purchaserPanel.add(postalField, c);
        c.gridx = 2;
        purchaserPanel.add(new JLabel("Province:"), c);
        c.gridx = 3;
        purchaserPanel.add(provinceField, c);
        c.gridx = 4;
        purchaserPanel.add(new JLabel("City:"), c);
        c.gridx = 5;
        purchaserPanel.add(cityField, c);
        c.gridx = 0; c.gridy++;
        purchaserPanel.add(new JLabel("Delivery Address:"), c);
        c.gridx = 1; c.gridwidth = 5;
        purchaserPanel.add(addressField, c);
        c.gridwidth = 1;
        c.gridx = 0; c.gridy++;
        purchaserPanel.add(new JLabel("Today's date:"), c);
        c.gridx = 1;
        purchaserPanel.add(dateField, c);
        c.gridx = 2;
        purchaserPanel.add(new JLabel("Credit Card No.:", SwingConstants.RIGHT), c);
        c.gridx = 3;
        purchaserPanel.add(ccField, c);
        c.gridx = 4;
        purchaserPanel.add(new JLabel("for dept use: validation id:"), c);
        c.gridx = 5;
        purchaserPanel.add(validationIdField, c);
        // Catalog Item Panel
        catalogPanel = new JPanel(new GridBagLayout());
        catalogPanel.setBorder(BorderFactory.createTitledBorder(BorderFactory.createEtchedBorder(), "Catalog Item", TitledBorder.LEFT, TitledBorder.TOP, null, Color.BLACK));
        GridBagConstraints cc = new GridBagConstraints();
        cc.insets = new Insets(2, 4, 2, 4);
        cc.fill = GridBagConstraints.HORIZONTAL;
        cc.gridx = 0; cc.gridy = 0;
        catalogPanel.add(new JLabel("Number:"), cc);
        cc.gridx = 1;
        catalogPanel.add(itemNumberField, cc);
        cc.gridx = 2;
        catalogPanel.add(new JLabel("Quantity:"), cc);
        cc.gridx = 3;
        catalogPanel.add(quantitySpinner, cc);
        cc.gridx = 4;
        catalogPanel.add(new JLabel("Cost/item:"), cc);
        cc.gridx = 5;
        catalogPanel.add(costField, cc);
        cc.gridx = 6;
        catalogPanel.add(new JLabel("Total:"), cc);
        cc.gridx = 7;
        catalogPanel.add(totalField, cc);
        cc.gridx = 0; cc.gridy++;
        catalogPanel.add(new JLabel("Balance Owing:"), cc);
        cc.gridx = 1;
        catalogPanel.add(balanceField, cc);
        btnPanel = new JPanel(new GridLayout(2, 1, 8, 8));
        btnPanel.add(nextItemBtn);
        btnPanel.add(triggerInvoiceBtn);
        cc.gridx = 6; cc.gridy = 1; cc.gridwidth = 2;
        catalogPanel.add(btnPanel, cc);
        cc.gridwidth = 1;
        centerPanel = new JPanel(new BorderLayout(8, 8));
        centerPanel.add(purchaserPanel, BorderLayout.NORTH);
        centerPanel.add(catalogPanel, BorderLayout.CENTER);
        add(centerPanel, BorderLayout.CENTER);
        revalidate(); repaint();
    }

    /**
     * Shows the catalog item entry screen (Screen 2).
     */
    private void showCatalogScreen() {
        getContentPane().removeAll();
        setLayout(new BorderLayout(8, 8));
        catalogPanel = new JPanel(new GridBagLayout());
        catalogPanel.setBorder(BorderFactory.createTitledBorder(BorderFactory.createEtchedBorder(), "Catalog Item", TitledBorder.LEFT, TitledBorder.TOP, null, Color.BLACK));
        GridBagConstraints cc = new GridBagConstraints();
        cc.insets = new Insets(2, 4, 2, 4);
        cc.fill = GridBagConstraints.HORIZONTAL;
        cc.gridx = 0; cc.gridy = 0;
        catalogPanel.add(new JLabel("Number:"), cc);
        cc.gridx = 1;
        catalogPanel.add(itemNumberField, cc);
        cc.gridx = 2;
        catalogPanel.add(new JLabel("Quantity:"), cc);
        cc.gridx = 3;
        catalogPanel.add(quantitySpinner, cc);
        cc.gridx = 4;
        catalogPanel.add(new JLabel("Cost/item:"), cc);
        cc.gridx = 5;
        catalogPanel.add(costField, cc);
        cc.gridx = 6;
        catalogPanel.add(new JLabel("Total:"), cc);
        cc.gridx = 7;
        catalogPanel.add(totalField, cc);
        cc.gridx = 0; cc.gridy++;
        catalogPanel.add(new JLabel("Balance Owing:"), cc);
        cc.gridx = 1;
        catalogPanel.add(balanceField, cc);
        btnPanel = new JPanel(new GridLayout(2, 1, 8, 8));
        btnPanel.add(nextItemBtn);
        btnPanel.add(triggerInvoiceBtn);
        cc.gridx = 6; cc.gridy = 1; cc.gridwidth = 2;
        catalogPanel.add(btnPanel, cc);
        cc.gridwidth = 1;
        add(catalogPanel, BorderLayout.CENTER);
        updateBalanceField();
        revalidate(); repaint();
    }

    /**
     * Calculates and updates the total field for the current catalog item.
     */
    private void updateTotalField() {
        try {
            int qty = (Integer) quantitySpinner.getValue();
            double cost = Double.parseDouble(costField.getText());
            double total = qty * cost;
            totalField.setText(String.format("%.2f", total));
        } catch (NumberFormatException e) {
            totalField.setText("");
            if (!costField.getText().trim().isEmpty()) {
                // Only show error if user has typed something
                showTemporaryError("Cost must be a valid number.");
            }
        }
    }

    /**
     * Shows a temporary error dialog for invalid input.
     * @param message The error message to display.
     */
    private void showTemporaryError(String message) {
        final JDialog dialog = new JDialog(this, "Input Error", true);
        dialog.setLayout(new BorderLayout());
        dialog.add(new JLabel(message, SwingConstants.CENTER), BorderLayout.CENTER);
        dialog.setSize(280, 100);
        dialog.setLocationRelativeTo(this);
        Timer timer = new Timer(1200, e -> dialog.dispose());
        timer.setRepeats(false);
        timer.start();
        dialog.setVisible(true);
    }

    /**
     * Validates all purchaser fields for correctness and completeness.
     * @return true if all purchaser fields are valid, false otherwise.
     */
    private boolean validatePurchaserFields() {
        if (nameField.getText().trim().isEmpty()) {
            showValidationError("Name is required.");
            return false;
        }
        if (!phoneField.getText().trim().matches("\\d{10,15}")) {
            showValidationError("Phone must be 10-15 digits (numbers only).");
            return false;
        }
        if (postalField.getText().trim().isEmpty()) {
            showValidationError("Postal code is required.");
            return false;
        }
        if (provinceField.getText().trim().isEmpty()) {
            showValidationError("Province is required.");
            return false;
        }
        if (cityField.getText().trim().isEmpty()) {
            showValidationError("City is required.");
            return false;
        }
        if (addressField.getText().trim().isEmpty()) {
            showValidationError("Delivery address is required.");
            return false;
        }
        if (!dateField.getText().trim().matches("\\d{2}/\\d{2}/\\d{4}")) {
            showValidationError("Date must be in MM/DD/YYYY format.");
            return false;
        }
        if (!ccField.getText().trim().matches("\\d{12,19}")) {
            showValidationError("Credit card must be 12-19 digits (numbers only).");
            return false;
        }
        // validationIdField is optional
        return true;
    }

    /**
     * Validates all catalog item fields for correctness and completeness.
     * @return true if all item fields are valid, false otherwise.
     */
    private boolean validateItemFields() {
        if (itemNumberField.getText().trim().isEmpty()) {
            showValidationError("Item number is required.");
            return false;
        }
        String costStr = costField.getText().trim();
        try {
            double cost = Double.parseDouble(costStr);
            if (cost < 0) {
                showValidationError("Cost must be non-negative.");
                return false;
            }
        } catch (NumberFormatException e) {
            showValidationError("Cost must be a valid number.");
            return false;
        }
        int qty = (Integer) quantitySpinner.getValue();
        if (qty < 1) {
            showValidationError("Quantity must be at least 1.");
            return false;
        }
        return true;
    }

    /**
     * Shows a validation error dialog with the given message.
     * @param message The error message to display.
     */
    private void showValidationError(String message) {
        JOptionPane.showMessageDialog(this, message, "Validation Error", JOptionPane.ERROR_MESSAGE);
    }

    /**
     * Adds the current catalog item to the list and updates the balance.
     * If purchaser info is not yet entered, validates and stores it.
     */
    private void addCatalogItem() {
        if (!purchaserInfoEntered) {
            if (!validatePurchaserFields()) return;
            purchaserInfo = new PurchaserInfo(
                nameField.getText().trim(),
                phoneField.getText().trim(),
                postalField.getText().trim(),
                provinceField.getText().trim(),
                cityField.getText().trim(),
                addressField.getText().trim(),
                dateField.getText().trim(),
                ccField.getText().trim(),
                validationIdField.getText().trim()
            );
            purchaserInfoEntered = true;
        }
        if (!validateItemFields()) return;
        String num = itemNumberField.getText().trim();
        int qty = (Integer) quantitySpinner.getValue();
        double cost = Double.parseDouble(costField.getText().trim());
        double total = qty * cost;
        items.add(new CatalogItem(num, qty, cost, total));
        balanceOwing += total;
        updateBalanceField();
        clearItemFields();
        showCatalogScreen();
    }

    /**
     * Clears all purchaser information fields.
     */
    private void clearPurchaserFields() {
        nameField.setText("");
        phoneField.setText("");
        postalField.setText("");
        provinceField.setText("");
        cityField.setText("");
        addressField.setText("");
        dateField.setText("");
        ccField.setText("");
        validationIdField.setText("");
    }

    /**
     * Shows the invoice dialog with all entered information and resets the application.
     */
    private void triggerInvoice() {
        if (items.isEmpty()) {
            showValidationError("No items entered.");
            return;
        }
        StringBuilder sb = new StringBuilder();
        sb.append("Invoice Summary\n\n");
        if (!purchaserInfoEntered || purchaserInfo == null) {
            sb.append("(No purchaser info entered)\n");
        } else {
            sb.append("Name: ").append(purchaserInfo.name).append("\n");
            sb.append("Phone: ").append(purchaserInfo.phone).append("\n");
            sb.append("Address: ").append(purchaserInfo.address).append("\n");
            sb.append("Date: ").append(purchaserInfo.date).append("\n");
            sb.append("Credit Card: ").append(purchaserInfo.cc).append("\n");
            sb.append("Validation ID: ").append(purchaserInfo.validationId).append("\n\n");
        }
        sb.append("Items:\n");
        for (CatalogItem item : items) {
            sb.append("  #").append(item.number).append("  Qty:").append(item.quantity)
              .append("  Cost:").append(String.format("%.2f", item.costPerItem))
              .append("  Total:").append(String.format("%.2f", item.total)).append("\n");
        }
        sb.append("\nBalance Owing: $").append(String.format("%.2f", balanceOwing));
        JOptionPane.showMessageDialog(this, sb.toString(), "Invoice", JOptionPane.INFORMATION_MESSAGE);
        // Reset
        items.clear();
        balanceOwing = 0.0;
        purchaserInfoEntered = false;
        purchaserInfo = null;
        clearPurchaserFields();
        clearItemFields();
        showPurchaserScreen();
    }

    /**
     * Updates the balance field with the current balance owing.
     */
    private void updateBalanceField() {
        if (balanceField != null)
            balanceField.setText(String.format("%.2f", balanceOwing));
    }

    /**
     * Clears all catalog item entry fields.
     */
    private void clearItemFields() {
        itemNumberField.setText("");
        quantitySpinner.setValue(1);
        costField.setText("");
        totalField.setText("");
    }

    /**
     * Main entry point. Sets the look and feel and launches the application.
     * @param args Command-line arguments (not used)
     */
    public static void main(String[] args) {
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception e) {
            // fallback
        }
        SwingUtilities.invokeLater(CheapShop::new);
    }

    /**
     * Data class representing a catalog item.
     */
    static class CatalogItem {
        /** Item number */
        String number;
        /** Quantity of the item */
        int quantity;
        /** Cost per item */
        double costPerItem;
        /** Total cost for this item */
        double total;
        /**
         * Constructs a CatalogItem.
         * @param n Item number
         * @param q Quantity
         * @param c Cost per item
         * @param t Total cost
         */
        CatalogItem(String n, int q, double c, double t) {
            number = n; quantity = q; costPerItem = c; total = t;
        }
    }

    /**
     * Data class representing purchaser information.
     */
    static class PurchaserInfo {
        /** Purchaser name */
        String name;
        /** Purchaser phone */
        String phone;
        /** Purchaser postal code */
        String postal;
        /** Purchaser province */
        String province;
        /** Purchaser city */
        String city;
        /** Purchaser address */
        String address;
        /** Date of purchase */
        String date;
        /** Credit card number */
        String cc;
        /** Validation ID (optional) */
        String validationId;
        /**
         * Constructs a PurchaserInfo object.
         * @param name Purchaser name
         * @param phone Purchaser phone
         * @param postal Purchaser postal code
         * @param province Purchaser province
         * @param city Purchaser city
         * @param address Purchaser address
         * @param date Date of purchase
         * @param cc Credit card number
         * @param validationId Validation ID (optional)
         */
        PurchaserInfo(String name, String phone, String postal, String province, String city, String address, String date, String cc, String validationId) {
            this.name = name;
            this.phone = phone;
            this.postal = postal;
            this.province = province;
            this.city = city;
            this.address = address;
            this.date = date;
            this.cc = cc;
            this.validationId = validationId;
        }
    }
}