/**
 * fft_analyzer.cpp
 * 
 * 実験データに対してFFT（高速フーリエ変換）を行うプログラム
 * 
 * 使い方:
 *   fft_analyzer <入力ファイル> [サンプリングレート(Hz)]
 * 
 * 入力フォーマット:
 *   - 1列: 振幅データのみ（1行に1つの数値）
 *   - 2列: 時間, 振幅（カンマまたはスペース区切り）
 *   - '#' で始まる行はコメントとしてスキップ
 * 
 * 出力:
 *   入力ファイル名_fft_result.csv に周波数スペクトルを出力
 * 
 * コンパイル:
 *   g++ -std=c++17 -O2 -o fft_analyzer fft_analyzer.cpp
 */

#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <complex>
#include <cmath>
#include <string>
#include <algorithm>
#include <iomanip>
#include <filesystem>

// --- 定数 ---
constexpr double PI = 3.14159265358979323846;

// --- 型定義 ---
using Complex = std::complex<double>;
using ComplexVec = std::vector<Complex>;

// ============================================================
// FFT (Cooley-Tukey アルゴリズム, 基数2, 反復版)
// ============================================================

/**
 * ビット反転並べ替え
 */
void bitReversalPermutation(ComplexVec& data) {
    size_t n = data.size();
    for (size_t i = 1, j = 0; i < n; ++i) {
        size_t bit = n >> 1;
        while (j & bit) {
            j ^= bit;
            bit >>= 1;
        }
        j ^= bit;
        if (i < j) {
            std::swap(data[i], data[j]);
        }
    }
}

/**
 * FFT本体（インプレース）
 * inverse = true で逆FFT
 */
void fft(ComplexVec& data, bool inverse = false) {
    size_t n = data.size();
    if (n <= 1) return;

    // ビット反転並べ替え
    bitReversalPermutation(data);

    // バタフライ演算
    for (size_t len = 2; len <= n; len <<= 1) {
        double angle = 2.0 * PI / static_cast<double>(len) * (inverse ? -1.0 : 1.0);
        Complex wlen(std::cos(angle), std::sin(angle));

        for (size_t i = 0; i < n; i += len) {
            Complex w(1.0, 0.0);
            for (size_t j = 0; j < len / 2; ++j) {
                Complex u = data[i + j];
                Complex v = data[i + j + len / 2] * w;
                data[i + j] = u + v;
                data[i + j + len / 2] = u - v;
                w *= wlen;
            }
        }
    }

    // 逆FFTの場合はNで割る
    if (inverse) {
        for (auto& x : data) {
            x /= static_cast<double>(n);
        }
    }
}

// ============================================================
// 窓関数
// ============================================================
enum class WindowType {
    RECTANGULAR,
    HANNING,
    HAMMING,
    BLACKMAN
};

/**
 * 窓関数を適用
 */
void applyWindow(std::vector<double>& data, WindowType type) {
    size_t n = data.size();
    if (n == 0) return;

    for (size_t i = 0; i < n; ++i) {
        double w = 1.0;
        double t = static_cast<double>(i) / static_cast<double>(n - 1);

        switch (type) {
            case WindowType::RECTANGULAR:
                w = 1.0;
                break;
            case WindowType::HANNING:
                w = 0.5 * (1.0 - std::cos(2.0 * PI * t));
                break;
            case WindowType::HAMMING:
                w = 0.54 - 0.46 * std::cos(2.0 * PI * t);
                break;
            case WindowType::BLACKMAN:
                w = 0.42 - 0.5 * std::cos(2.0 * PI * t) + 0.08 * std::cos(4.0 * PI * t);
                break;
        }
        data[i] *= w;
    }
}

// ============================================================
// データ読み込み
// ============================================================

/**
 * 行をトリムする
 */
std::string trim(const std::string& str) {
    size_t start = str.find_first_not_of(" \t\r\n");
    size_t end = str.find_last_not_of(" \t\r\n");
    if (start == std::string::npos) return "";
    return str.substr(start, end - start + 1);
}

/**
 * CSVまたはスペース区切りデータを読み込み
 * 戻り値: {時間ベクトル, 振幅ベクトル}
 * 時間データがない場合は空のベクトルを返す
 */
struct DataSet {
    std::vector<double> time;
    std::vector<double> amplitude;
};

DataSet loadData(const std::string& filename) {
    DataSet dataset;
    std::ifstream file(filename);

    if (!file.is_open()) {
        throw std::runtime_error("ファイルを開けません: " + filename);
    }

    std::string line;
    int lineNum = 0;

    while (std::getline(file, line)) {
        lineNum++;
        line = trim(line);

        // 空行・コメント行をスキップ
        if (line.empty() || line[0] == '#') continue;

        // カンマまたはスペース/タブ区切りで分割
        std::vector<double> values;
        std::stringstream ss(line);
        std::string token;

        // まずカンマで分割を試みる
        if (line.find(',') != std::string::npos) {
            while (std::getline(ss, token, ',')) {
                token = trim(token);
                if (!token.empty()) {
                    try {
                        values.push_back(std::stod(token));
                    } catch (const std::exception&) {
                        // ヘッダ行などは無視
                        values.clear();
                        break;
                    }
                }
            }
        } else {
            // スペース/タブ区切り
            double val;
            while (ss >> val) {
                values.push_back(val);
            }
        }

        if (values.empty()) continue;

        if (values.size() >= 2) {
            // 2列以上: (時間, 振幅) として扱う
            dataset.time.push_back(values[0]);
            dataset.amplitude.push_back(values[1]);
        } else if (values.size() == 1) {
            // 1列: 振幅のみ
            dataset.amplitude.push_back(values[0]);
        }
    }

    if (dataset.amplitude.empty()) {
        throw std::runtime_error("有効なデータが見つかりませんでした");
    }

    return dataset;
}

// ============================================================
// 2のべき乗にパディング
// ============================================================
size_t nextPowerOf2(size_t n) {
    size_t p = 1;
    while (p < n) p <<= 1;
    return p;
}

// ============================================================
// メイン処理
// ============================================================
int main(int argc, char* argv[]) {
    // --- 引数解析 ---
    if (argc < 2) {
        std::cerr << "使い方: " << argv[0] << " <入力ファイル> [サンプリングレート(Hz)] [窓関数]" << std::endl;
        std::cerr << std::endl;
        std::cerr << "オプション:" << std::endl;
        std::cerr << "  サンプリングレート: 周波数軸の計算に使用 (デフォルト: 1.0)" << std::endl;
        std::cerr << "  窓関数: rect, hanning, hamming, blackman (デフォルト: hanning)" << std::endl;
        std::cerr << std::endl;
        std::cerr << "入力フォーマット:" << std::endl;
        std::cerr << "  1列: 振幅データ (1行に1つの数値)" << std::endl;
        std::cerr << "  2列: 時間, 振幅 (カンマまたはスペース区切り)" << std::endl;
        std::cerr << "  '#' で始まる行はコメント" << std::endl;
        return 1;
    }

    std::string inputFile = argv[1];

    double samplingRate = 1.0;
    if (argc >= 3) {
        try {
            samplingRate = std::stod(argv[2]);
        } catch (const std::exception&) {
            std::cerr << "エラー: サンプリングレートが不正です: " << argv[2] << std::endl;
            return 1;
        }
    }

    // 窓関数の選択
    WindowType windowType = WindowType::HANNING;
    if (argc >= 4) {
        std::string winStr = argv[3];
        std::transform(winStr.begin(), winStr.end(), winStr.begin(), ::tolower);
        if (winStr == "rect" || winStr == "rectangular") {
            windowType = WindowType::RECTANGULAR;
        } else if (winStr == "hanning" || winStr == "hann") {
            windowType = WindowType::HANNING;
        } else if (winStr == "hamming") {
            windowType = WindowType::HAMMING;
        } else if (winStr == "blackman") {
            windowType = WindowType::BLACKMAN;
        } else {
            std::cerr << "警告: 不明な窓関数 '" << winStr << "', ハニング窓を使用します" << std::endl;
        }
    }

    // --- データ読み込み ---
    std::cout << "=== FFT Analyzer ===" << std::endl;
    std::cout << "入力ファイル: " << inputFile << std::endl;

    DataSet dataset;
    try {
        dataset = loadData(inputFile);
    } catch (const std::exception& e) {
        std::cerr << "エラー: " << e.what() << std::endl;
        return 1;
    }

    size_t originalSize = dataset.amplitude.size();
    std::cout << "データ点数: " << originalSize << std::endl;

    // サンプリングレートの自動推定（時間データがある場合）
    if (!dataset.time.empty() && dataset.time.size() >= 2) {
        double dt = (dataset.time.back() - dataset.time.front()) / static_cast<double>(dataset.time.size() - 1);
        if (dt > 0 && argc < 3) {
            samplingRate = 1.0 / dt;
            std::cout << "サンプリングレート (自動推定): " << samplingRate << " Hz" << std::endl;
        } else {
            std::cout << "サンプリングレート (指定値): " << samplingRate << " Hz" << std::endl;
        }
    } else {
        std::cout << "サンプリングレート: " << samplingRate << " Hz" << std::endl;
    }

    // --- 窓関数の適用 ---
    std::string windowName;
    switch (windowType) {
        case WindowType::RECTANGULAR: windowName = "矩形窓 (なし)"; break;
        case WindowType::HANNING:     windowName = "ハニング窓"; break;
        case WindowType::HAMMING:     windowName = "ハミング窓"; break;
        case WindowType::BLACKMAN:    windowName = "ブラックマン窓"; break;
    }
    std::cout << "窓関数: " << windowName << std::endl;
    applyWindow(dataset.amplitude, windowType);

    // --- ゼロパディング (2のべき乗に) ---
    size_t fftSize = nextPowerOf2(originalSize);
    std::cout << "FFTサイズ: " << fftSize << " (ゼロパディング: " << (fftSize - originalSize) << " 点追加)" << std::endl;

    // 複素数ベクトルに変換
    ComplexVec fftData(fftSize, Complex(0.0, 0.0));
    for (size_t i = 0; i < originalSize; ++i) {
        fftData[i] = Complex(dataset.amplitude[i], 0.0);
    }

    // --- FFT実行 ---
    std::cout << "FFT計算中..." << std::endl;
    fft(fftData);
    std::cout << "FFT計算完了!" << std::endl;

    // --- 結果計算と出力 ---
    double freqResolution = samplingRate / static_cast<double>(fftSize);
    size_t halfN = fftSize / 2 + 1;  // ナイキスト周波数まで

    // 出力ファイル名の生成
    std::filesystem::path inputPath(inputFile);
    std::string outputFile = inputPath.stem().string() + "_fft_result.csv";

    std::ofstream outFile(outputFile);
    if (!outFile.is_open()) {
        std::cerr << "エラー: 出力ファイルを作成できません: " << outputFile << std::endl;
        return 1;
    }

    // ヘッダ出力
    outFile << "# FFT Analysis Result" << std::endl;
    outFile << "# Input: " << inputFile << std::endl;
    outFile << "# Sampling Rate: " << samplingRate << " Hz" << std::endl;
    outFile << "# Window: " << windowName << std::endl;
    outFile << "# Data Points: " << originalSize << ", FFT Size: " << fftSize << std::endl;
    outFile << "# Frequency Resolution: " << freqResolution << " Hz" << std::endl;
    outFile << "#" << std::endl;
    outFile << "Frequency(Hz),Amplitude,Phase(rad),Power" << std::endl;

    // 最大振幅の検出（DC成分を除く）
    double maxAmplitude = 0.0;
    double maxFreq = 0.0;
    std::vector<std::pair<double, double>> peaks;  // (周波数, 振幅) のペア

    for (size_t i = 0; i < halfN; ++i) {
        double freq = static_cast<double>(i) * freqResolution;
        double amplitude = std::abs(fftData[i]) * 2.0 / static_cast<double>(originalSize);
        double phase = std::arg(fftData[i]);
        double power = amplitude * amplitude;

        // DC成分は2倍しない
        if (i == 0) amplitude /= 2.0;

        outFile << std::fixed << std::setprecision(6)
                << freq << ","
                << amplitude << ","
                << phase << ","
                << power << std::endl;

        // ピーク検出（DC除く）
        if (i > 0 && amplitude > maxAmplitude) {
            maxAmplitude = amplitude;
            maxFreq = freq;
        }
    }

    outFile.close();

    // --- コンソールに結果サマリーを表示 ---
    std::cout << std::endl;
    std::cout << "=== 結果サマリー ===" << std::endl;
    std::cout << "周波数分解能: " << std::fixed << std::setprecision(4) << freqResolution << " Hz" << std::endl;
    std::cout << "ナイキスト周波数: " << samplingRate / 2.0 << " Hz" << std::endl;
    std::cout << "最大ピーク周波数: " << std::setprecision(2) << maxFreq << " Hz (振幅: " << std::setprecision(6) << maxAmplitude << ")" << std::endl;

    // 上位ピークの検出と表示
    std::cout << std::endl;
    std::cout << "--- 主要ピーク (上位5つ) ---" << std::endl;

    // 振幅データを抽出してソート
    std::vector<std::pair<double, double>> freqAmplitudes;
    for (size_t i = 1; i < halfN; ++i) {
        double freq = static_cast<double>(i) * freqResolution;
        double amplitude = std::abs(fftData[i]) * 2.0 / static_cast<double>(originalSize);
        freqAmplitudes.emplace_back(freq, amplitude);
    }

    // 振幅でソート（降順）
    std::sort(freqAmplitudes.begin(), freqAmplitudes.end(),
              [](const auto& a, const auto& b) { return a.second > b.second; });

    // 上位5つのピークを表示（近接ピークは除外）
    int peakCount = 0;
    std::vector<double> foundPeaks;
    for (const auto& [freq, amp] : freqAmplitudes) {
        if (peakCount >= 5) break;

        // 既に見つけたピークの近くは除外
        bool tooClose = false;
        for (double fp : foundPeaks) {
            if (std::abs(freq - fp) < freqResolution * 3) {
                tooClose = true;
                break;
            }
        }
        if (tooClose) continue;

        std::cout << "  " << (peakCount + 1) << ". "
                  << std::fixed << std::setprecision(2) << freq << " Hz"
                  << "  (振幅: " << std::setprecision(6) << amp << ")" << std::endl;
        foundPeaks.push_back(freq);
        peakCount++;
    }

    std::cout << std::endl;
    std::cout << "結果を '" << outputFile << "' に保存しました" << std::endl;

    return 0;
}
