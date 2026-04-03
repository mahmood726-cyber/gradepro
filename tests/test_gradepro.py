"""Selenium tests for GRADEPro — GRADE Summary of Findings generator."""
import sys, io, os, unittest, time, math

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

HTML = 'file:///' + os.path.abspath(r'C:\Models\GRADEPro\gradepro.html').replace('\\', '/')


class TestGRADEPro(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        opts = Options()
        opts.add_argument('--headless=new')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-gpu')
        opts.add_argument('--window-size=1400,900')
        cls.drv = webdriver.Chrome(options=opts)
        cls.drv.get(HTML)
        time.sleep(1.5)
        # Clear any saved state to start fresh
        cls.drv.execute_script("localStorage.removeItem('gradepro_state_v1');")
        cls.drv.get(HTML)
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.drv.quit()

    def js(self, script):
        return self.drv.execute_script(script)

    # ================================================================
    # 1. computeCertainty — RCT baseline
    # ================================================================
    def test_01_certainty_rct_high(self):
        """RCT with no downgrades = HIGH (4)."""
        val = self.js("""
            var oc = {
                domains: {rob:0, inconsistency:0, indirectness:0, imprecision:0, pub_bias:0},
                upgrades: {large_effect:0, dose_response:0, confounding:0}
            };
            return computeCertainty(oc, 'RCT');
        """)
        self.assertEqual(val, 4)

    # ================================================================
    # 2. computeCertainty — single downgrade
    # ================================================================
    def test_02_certainty_rct_one_downgrade(self):
        """RCT with imprecision -1 = MODERATE (3)."""
        val = self.js("""
            var oc = {
                domains: {rob:0, inconsistency:0, indirectness:0, imprecision:-1, pub_bias:0},
                upgrades: {large_effect:0, dose_response:0, confounding:0}
            };
            return computeCertainty(oc, 'RCT');
        """)
        self.assertEqual(val, 3)

    # ================================================================
    # 3. computeCertainty — two downgrades
    # ================================================================
    def test_03_certainty_rct_two_downgrades(self):
        """RCT with inconsistency -1 + imprecision -1 = LOW (2)."""
        val = self.js("""
            var oc = {
                domains: {rob:0, inconsistency:-1, indirectness:0, imprecision:-1, pub_bias:0},
                upgrades: {large_effect:0, dose_response:0, confounding:0}
            };
            return computeCertainty(oc, 'RCT');
        """)
        self.assertEqual(val, 2)

    # ================================================================
    # 4. computeCertainty — clamp to minimum 1
    # ================================================================
    def test_04_certainty_floor(self):
        """RCT with all domains very serious still clamps to 1."""
        val = self.js("""
            var oc = {
                domains: {rob:-2, inconsistency:-2, indirectness:-2, imprecision:-2, pub_bias:-2},
                upgrades: {large_effect:0, dose_response:0, confounding:0}
            };
            return computeCertainty(oc, 'RCT');
        """)
        self.assertEqual(val, 1)

    # ================================================================
    # 5. computeCertainty — observational baseline
    # ================================================================
    def test_05_certainty_obs_baseline(self):
        """OBS with no downgrades starts at LOW (2)."""
        val = self.js("""
            var oc = {
                domains: {rob:0, inconsistency:0, indirectness:0, imprecision:0, pub_bias:0},
                upgrades: {large_effect:0, dose_response:0, confounding:0}
            };
            return computeCertainty(oc, 'OBS');
        """)
        self.assertEqual(val, 2)

    # ================================================================
    # 6. computeCertainty — OBS with upgrades
    # ================================================================
    def test_06_certainty_obs_with_upgrades(self):
        """OBS + large_effect +1 + dose_response +1 = HIGH (4)."""
        val = self.js("""
            var oc = {
                domains: {rob:0, inconsistency:0, indirectness:0, imprecision:0, pub_bias:0},
                upgrades: {large_effect:1, dose_response:1, confounding:0}
            };
            return computeCertainty(oc, 'OBS');
        """)
        self.assertEqual(val, 4)

    # ================================================================
    # 7. computeCertainty — cap at 4
    # ================================================================
    def test_07_certainty_cap(self):
        """RCT + all upgrades still capped at 4."""
        val = self.js("""
            var oc = {
                domains: {rob:0, inconsistency:0, indirectness:0, imprecision:0, pub_bias:0},
                upgrades: {large_effect:1, dose_response:1, confounding:1}
            };
            return computeCertainty(oc, 'RCT');
        """)
        self.assertEqual(val, 4)

    # ================================================================
    # 8. calcAbsoluteEffects — RR
    # ================================================================
    def test_08_absolute_effects_rr(self):
        """RR=0.60, controlRate=0.02: absolute effects correct."""
        result = self.js("""
            var oc = {measure:'RR', estimate:0.60, ci_lower:0.41, ci_upper:0.88, controlRate:0.02};
            return calcAbsoluteEffects(oc);
        """)
        self.assertEqual(result['type'], 'binary')
        self.assertEqual(result['without'], 20)  # 0.02 * 1000
        self.assertEqual(result['with_est'], 12)  # 0.02 * 0.60 * 1000 = 12
        self.assertEqual(result['diff'], -8)      # (0.012 - 0.02) * 1000 = -8

    # ================================================================
    # 9. calcAbsoluteEffects — OR
    # ================================================================
    def test_09_absolute_effects_or(self):
        """OR with controlRate uses correct OR-to-probability formula."""
        result = self.js("""
            var oc = {measure:'OR', estimate:2.0, ci_lower:1.2, ci_upper:3.5, controlRate:0.10};
            return calcAbsoluteEffects(oc);
        """)
        self.assertEqual(result['type'], 'binary')
        self.assertEqual(result['without'], 100)  # 0.10 * 1000
        # with = (2.0 * 0.10) / (1 - 0.10 + 2.0 * 0.10) = 0.2/1.1 ~ 0.1818 -> 182
        self.assertEqual(result['with_est'], 182)

    # ================================================================
    # 10. calcAbsoluteEffects — SMD (continuous)
    # ================================================================
    def test_10_absolute_effects_smd(self):
        """SMD returns continuous type with md values."""
        result = self.js("""
            var oc = {measure:'SMD', estimate:-0.62, ci_lower:-0.81, ci_upper:-0.42, controlRate:null};
            return calcAbsoluteEffects(oc);
        """)
        self.assertEqual(result['type'], 'continuous')
        self.assertAlmostEqual(result['md'], -0.62, places=2)
        self.assertEqual(result['measure'], 'SMD')

    # ================================================================
    # 11. calcAbsoluteEffects — RR without controlRate returns null
    # ================================================================
    def test_11_absolute_effects_rr_no_cr(self):
        """RR without controlRate returns null."""
        result = self.js("""
            var oc = {measure:'RR', estimate:0.80, ci_lower:0.70, ci_upper:0.92, controlRate:null};
            return calcAbsoluteEffects(oc);
        """)
        self.assertIsNone(result)

    # ================================================================
    # 12. getSignificance — ratio (crossing 1)
    # ================================================================
    def test_12_significance_ratio_crossing_null(self):
        """RR CI crossing 1 -> not significant."""
        val = self.js("""
            return getSignificance({measure:'RR', ci_lower:0.74, ci_upper:1.05});
        """)
        self.assertFalse(val)

    # ================================================================
    # 13. getSignificance — ratio (not crossing 1)
    # ================================================================
    def test_13_significance_ratio_significant(self):
        """RR CI not crossing 1 -> significant."""
        val = self.js("""
            return getSignificance({measure:'RR', ci_lower:0.41, ci_upper:0.88});
        """)
        self.assertTrue(val)

    # ================================================================
    # 14. getSignificance — continuous
    # ================================================================
    def test_14_significance_continuous_crossing_zero(self):
        """SMD CI crossing 0 -> not significant."""
        val = self.js("""
            return getSignificance({measure:'SMD', ci_lower:-0.20, ci_upper:0.15});
        """)
        self.assertFalse(val)

    # ================================================================
    # 15. getDirection
    # ================================================================
    def test_15_direction(self):
        """RR<1 reduces; MD<0 reduces."""
        val_rr = self.js("return getDirection({measure:'RR', estimate:0.60});")
        self.assertEqual(val_rr, 'reduces')
        val_smd = self.js("return getDirection({measure:'SMD', estimate:0.35});")
        self.assertEqual(val_smd, 'increases')

    # ================================================================
    # 16. generatePlainLanguage
    # ================================================================
    def test_16_plain_language_high_significant(self):
        """HIGH + significant -> direct statement."""
        text = self.js("""
            var oc = {measure:'RR', estimate:0.44, ci_lower:0.26, ci_upper:0.74};
            return generatePlainLanguage(oc, 4, 'DOACs', 'intracranial haemorrhage');
        """)
        self.assertIn('DOACs', text)
        self.assertIn('reduces', text)
        # HIGH certainty = no hedging word
        self.assertNotIn('probably', text)
        self.assertNotIn('may', text)

    # ================================================================
    # 17. generatePlainLanguage — moderate + non-significant
    # ================================================================
    def test_17_plain_language_moderate_nonsig(self):
        """MODERATE + non-significant -> 'probably little to no difference'."""
        text = self.js("""
            var oc = {measure:'RR', estimate:0.98, ci_lower:0.82, ci_upper:1.17};
            return generatePlainLanguage(oc, 3, 'DOACs', 'mortality');
        """)
        self.assertIn('probably', text)
        self.assertIn('little to no difference', text)

    # ================================================================
    # 18. generatePlainLanguage — very low certainty
    # ================================================================
    def test_18_plain_language_very_low(self):
        """VERY_LOW -> 'very uncertain'."""
        text = self.js("""
            var oc = {measure:'RR', estimate:0.70, ci_lower:0.40, ci_upper:1.20};
            return generatePlainLanguage(oc, 1, 'Drug X', 'outcome Y');
        """)
        self.assertIn('very uncertain', text)

    # ================================================================
    # 19. autoSuggestDomains — inconsistency
    # ================================================================
    def test_19_autosuggest_inconsistency(self):
        """I2=72% with k>=3 suggests Serious."""
        sugg = self.js("""
            var oc = {i2:72, k:6, eggerP:null, measure:'RR', estimate:0.88,
                      ci_lower:0.74, ci_upper:1.05, totalN:5000, controlRate:0.03,
                      mcid:null, mcidRatio:null};
            return autoSuggestDomains(oc);
        """)
        self.assertIn('inconsistency', sugg)
        self.assertIn('Serious', sugg['inconsistency'])

    # ================================================================
    # 20. autoSuggestDomains — I2 unreliable with k<3
    # ================================================================
    def test_20_autosuggest_inconsistency_k_small(self):
        """k<3 -> I2 unreliable."""
        sugg = self.js("""
            var oc = {i2:50, k:2, eggerP:null, measure:'RR', estimate:0.88,
                      ci_lower:0.74, ci_upper:1.05, totalN:500, controlRate:0.03,
                      mcid:null, mcidRatio:null};
            return autoSuggestDomains(oc);
        """)
        self.assertIn('unreliable', sugg['inconsistency'])

    # ================================================================
    # 21. autoSuggestDomains — pub bias (k<10)
    # ================================================================
    def test_21_autosuggest_pub_bias_k_small(self):
        """k<10 -> funnel test unreliable."""
        sugg = self.js("""
            var oc = {i2:10, k:5, eggerP:0.04, measure:'RR', estimate:0.88,
                      ci_lower:0.74, ci_upper:1.05, totalN:5000, controlRate:0.03,
                      mcid:null, mcidRatio:null};
            return autoSuggestDomains(oc);
        """)
        self.assertIn('pub_bias', sugg)
        self.assertIn('unreliable', sugg['pub_bias'])

    # ================================================================
    # 22. autoSuggestDomains — pub bias (k>=10, Egger sig)
    # ================================================================
    def test_22_autosuggest_pub_bias_egger_sig(self):
        """k>=10 + Egger p<0.10 -> Consider Serious."""
        sugg = self.js("""
            var oc = {i2:10, k:15, eggerP:0.04, measure:'RR', estimate:0.88,
                      ci_lower:0.74, ci_upper:1.05, totalN:8000, controlRate:0.03,
                      mcid:null, mcidRatio:null};
            return autoSuggestDomains(oc);
        """)
        self.assertIn('Serious', sugg['pub_bias'])

    # ================================================================
    # 23. Load VTE example dataset
    # ================================================================
    def test_23_load_example_vte(self):
        """Load VTE example and verify 4 outcomes appear."""
        self.js("loadExample('vte_anticoag');")
        time.sleep(0.5)
        count = self.js("return state.outcomes.length;")
        self.assertEqual(count, 4)
        name = self.js("return state.intervention;")
        self.assertEqual(name, "Direct oral anticoagulants")

    # ================================================================
    # 24. Load COVID steroids example
    # ================================================================
    def test_24_load_example_covid(self):
        """Load COVID example: 3 outcomes, design=RCT."""
        self.js("loadExample('covid_steroids');")
        time.sleep(0.5)
        count = self.js("return state.outcomes.length;")
        self.assertEqual(count, 3)
        design = self.js("return state.design;")
        self.assertEqual(design, 'RCT')

    # ================================================================
    # 25. Load exercise example
    # ================================================================
    def test_25_load_example_exercise(self):
        """Exercise example: first outcome has dose_response=1."""
        self.js("loadExample('exercise_depression');")
        time.sleep(0.5)
        up = self.js("return state.outcomes[0].upgrades.dose_response;")
        self.assertEqual(up, 1)

    # ================================================================
    # 26. VTE certainty calculations
    # ================================================================
    def test_26_vte_certainty_values(self):
        """VTE outcomes: first=MODERATE (imprecision), last=HIGH."""
        self.js("loadExample('vte_anticoag');")
        time.sleep(0.3)
        # First outcome: imprecision -1 -> MODERATE (3)
        cert1 = self.js("return computeCertainty(state.outcomes[0], state.design);")
        self.assertEqual(cert1, 3)
        # Last outcome (ICH): no downgrades -> HIGH (4)
        cert4 = self.js("return computeCertainty(state.outcomes[3], state.design);")
        self.assertEqual(cert4, 4)

    # ================================================================
    # 27. Tab switching
    # ================================================================
    def test_27_tab_switching(self):
        """Switch to SoF tab, verify panel is active."""
        self.js("switchTab('sof');")
        time.sleep(0.3)
        active = self.js("return document.getElementById('tab-sof').classList.contains('active');")
        self.assertTrue(active)
        # Switch back
        self.js("switchTab('entry');")
        time.sleep(0.3)
        active2 = self.js("return document.getElementById('tab-entry').classList.contains('active');")
        self.assertTrue(active2)

    # ================================================================
    # 28. SoF table rendering
    # ================================================================
    def test_28_sof_table_rows(self):
        """SoF tab shows correct number of rows after loading example."""
        self.js("loadExample('vte_anticoag');")
        time.sleep(0.3)
        self.js("switchTab('sof');")
        time.sleep(0.5)
        rows = self.js("return document.getElementById('sofTbody').children.length;")
        self.assertEqual(rows, 4)

    # ================================================================
    # 29. buildCsv
    # ================================================================
    def test_29_build_csv(self):
        """CSV export has correct header row and data rows."""
        self.js("loadExample('vte_anticoag');")
        time.sleep(0.3)
        csv = self.js("return buildCsv();")
        lines = csv.strip().split('\n')
        self.assertGreaterEqual(len(lines), 5)  # 1 header + 4 outcomes
        self.assertIn('Outcome', lines[0])
        self.assertIn('Certainty', lines[0])

    # ================================================================
    # 30. buildNarrative
    # ================================================================
    def test_30_build_narrative(self):
        """Narrative text includes intervention and outcome names."""
        self.js("loadExample('covid_steroids');")
        time.sleep(0.3)
        text = self.js("return buildNarrative();")
        self.assertIn('Dexamethasone', text)
        self.assertIn('28-day mortality', text)
        self.assertIn('High', text)

    # ================================================================
    # 31. buildSofHtml
    # ================================================================
    def test_31_build_sof_html(self):
        """SoF HTML export includes table tags."""
        self.js("loadExample('vte_anticoag');")
        time.sleep(0.3)
        html = self.js("return buildSofHtml(true);")
        self.assertIn('<table', html)
        self.assertIn('Recurrent VTE', html)

    # ================================================================
    # 32. escHtml
    # ================================================================
    def test_32_esc_html(self):
        """escHtml escapes quotes, ampersands, angle brackets."""
        val = self.js("""return escHtml('<script>"test" & \\'more\\'');""")
        self.assertIn('&lt;', val)
        self.assertIn('&amp;', val)
        self.assertIn('&quot;', val)
        self.assertIn('&#39;', val)

    # ================================================================
    # 33. csvEsc — formula injection guard
    # ================================================================
    def test_33_csv_esc_injection(self):
        """csvEsc prepends ' to cells starting with =."""
        val = self.js("return csvEsc('=SUM(A1:A10)');")
        self.assertTrue(val.startswith("'"))
        # Negative numbers NOT prefixed
        val2 = self.js("return csvEsc('-0.5 mmHg');")
        self.assertFalse(val2.startswith("'"))

    # ================================================================
    # 34. fmtNum
    # ================================================================
    def test_34_fmtnum(self):
        """fmtNum rounds correctly for various magnitudes."""
        self.assertEqual(self.js("return fmtNum(15.6789);"), '15.68')
        self.assertEqual(self.js("return fmtNum(2.345);"), '2.35')
        self.assertEqual(self.js("return fmtNum(0.0412);"), '0.041')
        self.assertEqual(self.js("return fmtNum(null);"), '\u2014')

    # ================================================================
    # 35. calcAbsoluteEffects — HR (approximate flag)
    # ================================================================
    def test_35_absolute_effects_hr_approximate(self):
        """HR absolute effects are marked approximate."""
        result = self.js("""
            var oc = {measure:'HR', estimate:0.80, ci_lower:0.70, ci_upper:0.92, controlRate:0.25};
            return calcAbsoluteEffects(oc);
        """)
        self.assertTrue(result['approximate'])
        self.assertEqual(result['type'], 'binary')

    # ================================================================
    # 36. calcAbsoluteEffects — Risk Difference (RD)
    # ================================================================
    def test_36_absolute_effects_rd(self):
        """RD absolute effects: without=CR*1000, with_est=(CR+RD)*1000."""
        result = self.js("""
            var oc = {measure:'RD', estimate:-0.05, ci_lower:-0.08, ci_upper:-0.02, controlRate:0.15};
            return calcAbsoluteEffects(oc);
        """)
        self.assertEqual(result['type'], 'binary')
        self.assertEqual(result['without'], 150)
        self.assertEqual(result['with_est'], 100)  # (0.15 + -0.05) * 1000 = 100
        self.assertEqual(result['diff'], -50)

    # ================================================================
    # 37. Add outcome row
    # ================================================================
    def test_37_add_outcome_row(self):
        """Clicking add row increases outcome count."""
        # Reset first
        self.js("""
            state = {intervention:'', comparator:'', condition:'', design:'RCT', outcomes:[]};
            state.outcomes.push(makeOutcome(genId()));
            renderOutcomesTable();
        """)
        time.sleep(0.3)
        before = self.js("return state.outcomes.length;")
        self.js("state.outcomes.push(makeOutcome(genId())); renderOutcomesTable();")
        time.sleep(0.3)
        after = self.js("return state.outcomes.length;")
        self.assertEqual(after, before + 1)

    # ================================================================
    # 38. Theme toggle
    # ================================================================
    def test_38_theme_toggle(self):
        """Theme toggle switches light class on body."""
        self.js("document.getElementById('btnTheme').click();")
        time.sleep(0.3)
        has_light = self.js("return document.body.classList.contains('light');")
        # Toggle again
        self.js("document.getElementById('btnTheme').click();")
        time.sleep(0.3)
        has_light2 = self.js("return document.body.classList.contains('light');")
        self.assertNotEqual(has_light, has_light2)

    # ================================================================
    # 39. CERT_SYMBOLS mapping
    # ================================================================
    def test_39_cert_symbols(self):
        """CERT_SYMBOLS has 4 entries with correct oplus patterns."""
        count = self.js("return Object.keys(CERT_SYMBOLS).length;")
        self.assertEqual(count, 4)
        sym4 = self.js("return CERT_SYMBOLS[4];")
        self.assertEqual(len(sym4), 4)  # 4 oplus chars

    # ================================================================
    # 40. autoSuggestDomains — imprecision for continuous with MCID
    # ================================================================
    def test_40_autosuggest_imprecision_smd_mcid(self):
        """SMD CI crossing 0 -> Serious imprecision."""
        sugg = self.js("""
            var oc = {i2:10, k:5, eggerP:null, measure:'SMD', estimate:-0.30,
                      ci_lower:-0.65, ci_upper:0.05, totalN:200, controlRate:null,
                      mcid:0.5, mcidRatio:null};
            return autoSuggestDomains(oc);
        """)
        self.assertIn('imprecision', sugg)
        self.assertIn('Serious', sugg['imprecision'])

    # ================================================================
    # 41. Large effect auto-suggestion for OBS
    # ================================================================
    def test_41_autosuggest_large_effect_obs(self):
        """OBS with RR >= 2 suggests large effect upgrade."""
        sugg = self.js("""
            state.design = 'OBS';
            var oc = {i2:10, k:5, eggerP:null, measure:'RR', estimate:3.0,
                      ci_lower:2.1, ci_upper:4.3, totalN:5000, controlRate:0.05,
                      mcid:null, mcidRatio:null};
            var s = autoSuggestDomains(oc);
            state.design = 'RCT';
            return s;
        """)
        self.assertIn('large_effect', sugg)
        self.assertIn('upgrade', sugg['large_effect'].lower())

    # ================================================================
    # 42. Grade tab rendering with outcomes
    # ================================================================
    def test_42_grade_tab_renders(self):
        """Grade tab populates domain cards."""
        self.js("loadExample('vte_anticoag');")
        time.sleep(0.3)
        self.js("switchTab('grade');")
        time.sleep(0.5)
        container = self.js("return document.getElementById('domainsContainer').children.length;")
        self.assertGreaterEqual(container, 5)  # 5 GRADE domains

    # ================================================================
    # 43. Certainty badge updates
    # ================================================================
    def test_43_certainty_badge(self):
        """certBadge text includes certainty level."""
        self.js("loadExample('vte_anticoag');")
        time.sleep(0.3)
        self.js("switchTab('grade');")
        time.sleep(0.5)
        badge_text = self.js("return document.getElementById('certBadge').textContent;")
        # First VTE outcome: imprecision -1 -> MODERATE
        self.assertIn('MODERATE', badge_text)

    # ================================================================
    # 44. Exercise example certainty checks
    # ================================================================
    def test_44_exercise_certainty(self):
        """Exercise outcomes: o1 has rob-1, inconsistency-1, pub_bias-1, dose_response+1 -> LOW (2)."""
        self.js("loadExample('exercise_depression');")
        time.sleep(0.3)
        cert = self.js("return computeCertainty(state.outcomes[0], state.design);")
        # base 4, rob -1, inconsistency -1, pub_bias -1, dose_response +1 = 2
        self.assertEqual(cert, 2)

    # ================================================================
    # 45. makeOutcome default values
    # ================================================================
    def test_45_make_outcome_defaults(self):
        """makeOutcome returns proper default structure."""
        oc = self.js("return makeOutcome('test_id');")
        self.assertEqual(oc['id'], 'test_id')
        self.assertEqual(oc['measure'], 'RR')
        self.assertIsNone(oc['estimate'])
        self.assertEqual(oc['domains']['rob'], 0)
        self.assertEqual(oc['upgrades']['large_effect'], 0)


if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    unittest.main(verbosity=2)
