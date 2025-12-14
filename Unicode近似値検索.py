#!/usr/bin/env python3
# Unicode近傍文字表示ツール（最終統合版）
# 方針:
#  - 主役は「必ず可視な文字表現」
#  - 前後N個の文字を列挙
#  - コードポイント表示はオプション
#  - UTF-8 / UTF-16 / UTF-32 の表現を切り替え表示可能
#  - 不可視文字は必ず可視化

import argparse
import sys
import unicodedata

# Control Pictures (U+2400–U+243F)
CONTROL_PICTURES_BASE = 0x2400


def visualize_char(cp: int) -> str:
    """不可視文字を可視表現に変換"""
    ch = chr(cp)

    cat = unicodedata.category(ch)

    # 制御文字 (Cc)
    if cat == "Cc":
        if cp <= 0x1F:
            return chr(CONTROL_PICTURES_BASE + cp)
        if cp == 0x7F:
            return chr(CONTROL_PICTURES_BASE + 0x7F)
        return f"<U+{cp:04X}>"

    # フォーマット文字 (Cf): ZWJ / ZWSP / BOM など
    if cat == "Cf":
        return f"<{unicodedata.name(ch, 'FORMAT')}>"

    # 通常表示可能
    if ch.isprintable():
        return ch

    return f"<U+{cp:04X}>"


def encode_repr(cp: int, mode: str) -> str:
    """指定エンコーディングでの数値表現を返す"""
    ch = chr(cp)

    if mode == "utf8":
        b = ch.encode("utf-8")
        return "UTF-8: " + " ".join(f"{x:02X}" for x in b)

    if mode == "utf16":
        b = ch.encode("utf-16-be")
        units = [b[i:i+2] for i in range(0, len(b), 2)]
        return "UTF-16: " + " ".join(f"{int.from_bytes(u, 'big'):04X}" for u in units)

    if mode == "utf32":
        return f"UTF-32: {cp:08X}"

    return ""


def main(argv):
    parser = argparse.ArgumentParser(
        description="指定文字の前後N個のUnicode文字を可視化表示"
    )
    parser.add_argument("char", help="基準となる1文字")
    parser.add_argument("count", type=int, help="前後に表示する文字数")

    # オプション類
    parser.add_argument(
        "--codepoint",
        action="store_true",
        help="Unicodeコードポイント (U+XXXX) を表示"
    )
    parser.add_argument(
        "--encoding",
        choices=["utf8", "utf16", "utf32"],
        help="指定エンコーディングでの数値表現を表示"
    )

    args = parser.parse_args(argv)

    if len(args.char) != 1:
        print("エラー: 基準文字は1文字にしてください")
        return

    base_cp = ord(args.char)
    start = max(0, base_cp - args.count)
    end = min(0x10FFFF, base_cp + args.count)

    for cp in range(start, end + 1):
        mark = "<= " if cp == base_cp else "   "
        vis = visualize_char(cp)

        line = f"{mark}{vis}"

        if args.codepoint:
            line += f"  U+{cp:06X}"

        if args.encoding:
            line += "  " + encode_repr(cp, args.encoding)

        print(line)


if __name__ == '__main__':
    main(sys.argv[1:])