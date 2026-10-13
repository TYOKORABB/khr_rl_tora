// khr_core.h（通信監視の状態機械と状態語）のホスト上の単体テスト。
// ファームのフレーム周期（10 ms）で時間を進め、パケットの到着パターンごとに状態遷移を確かめる。
//
//   g++ -std=c++17 -Wall -Wextra -Werror -I <パッチ適用後の src> test_khr_core.cpp -o test_khr_core && ./test_khr_core
//   （build_fw.sh --test が上を実行する）

#include "khr_core.h"

#include <cstdio>
#include <cstdlib>

static int g_fail = 0;

#define CHECK(cond, ...)                                       \
  do {                                                         \
    if (!(cond)) {                                             \
      std::printf("  NG %s:%d  ", __FILE__, __LINE__);         \
      std::printf(__VA_ARGS__);                                \
      std::printf("\n");                                       \
      g_fail++;                                                \
    }                                                          \
  } while (0)

static const uint32_t TIMEOUT = 200, HOLD = 1000, FRAME = 10;
static const bool POWER_ON = false, POWER_OFF = true;

// 10 ms ごとに update を呼び、最後の状態を返す。packet(t) が true のフレームでパケットが届く。
// power_off: 届くパケットが全サーボ電源 OFF（コンソールの Power を切った状態）か。
template <class F>
static uint8_t run(KhrWatchdog &w, uint32_t &t, uint32_t dur, F packet, bool power_off) {
  const uint32_t end = t + dur;
  uint8_t s = w.state;
  for (; t != end; t += FRAME) {
    const bool fresh = packet(t);
    s = w.update(t, fresh, fresh && power_off);
  }
  return s;
}

static bool always(uint32_t) { return true; }
static bool never(uint32_t) { return false; }

// 通常の起動手順: コンソールが Power OFF で起動 → 操作者が Power ON → 1 秒動かした状態
static KhrWatchdog running(uint32_t &t) {
  KhrWatchdog w(TIMEOUT, HOLD);
  run(w, t, 500, always, POWER_OFF);
  run(w, t, 1000, always, POWER_ON);
  return w;
}

int main() {
  std::printf("[1] 起動後、パケットが来なければ DISARMED（全サーボ脱力）のまま\n");
  {
    KhrWatchdog w(TIMEOUT, HOLD);
    uint32_t t = 0;
    CHECK(run(w, t, 10000, never, POWER_OFF) == KHR_WDG_DISARMED, "state=%d", w.state);
  }

  std::printf("[2] 起動後の最初のパケットが Power ON なら DISARMED のまま（ESP32 の再起動でいきなり動かない）\n");
  {
    KhrWatchdog w(TIMEOUT, HOLD);
    uint32_t t = 3000;
    CHECK(run(w, t, 5000, always, POWER_ON) == KHR_WDG_DISARMED, "state=%d", w.state);
    CHECK(run(w, t, FRAME, always, POWER_OFF) == KHR_WDG_OK, "Power OFF で抜けない state=%d", w.state);
    CHECK(run(w, t, 60000, always, POWER_ON) == KHR_WDG_OK, "その後の Power ON で state=%d", w.state);
  }

  std::printf("[3] 途絶: 190 ms は OK、200 ms で HOLD、1190 ms は HOLD、1200 ms で LIMP\n");
  {
    uint32_t t = 0;
    KhrWatchdog w = running(t);
    const uint32_t last = t - FRAME; // 最後にパケットが来た時刻
    uint32_t t_hold = 0, t_limp = 0;
    for (; t < last + 3000; t += FRAME) {
      const uint8_t s = w.update(t, false, false);
      if (s == KHR_WDG_HOLD && !t_hold) t_hold = t - last;
      if (s == KHR_WDG_LIMP && !t_limp) t_limp = t - last;
    }
    CHECK(t_hold == TIMEOUT, "HOLD に入った途絶時間 = %u ms（期待 %u）", t_hold, TIMEOUT);
    CHECK(t_limp == TIMEOUT + HOLD, "LIMP に入った途絶時間 = %u ms（期待 %u）", t_limp, TIMEOUT + HOLD);
    CHECK(w.state == KHR_WDG_LIMP, "state=%d", w.state);
  }

  std::printf("[4] HOLD 中にパケットが戻れば OK に戻る（短い途絶では脱力しない）\n");
  {
    uint32_t t = 0;
    KhrWatchdog w = running(t);
    CHECK(run(w, t, 800, never, POWER_ON) == KHR_WDG_HOLD, "state=%d", w.state);
    CHECK(run(w, t, FRAME, always, POWER_ON) == KHR_WDG_OK, "state=%d", w.state);
  }

  std::printf("[5] LIMP はパケットが戻っても Power ON のままなら解けない\n");
  {
    uint32_t t = 0;
    KhrWatchdog w = running(t);
    run(w, t, 2000, never, POWER_ON);
    CHECK(w.state == KHR_WDG_LIMP, "state=%d", w.state);
    CHECK(run(w, t, 5000, always, POWER_ON) == KHR_WDG_LIMP, "state=%d", w.state);
  }

  std::printf("[6] LIMP は Power OFF のパケットで解け、その後は通常どおり\n");
  {
    uint32_t t = 0;
    KhrWatchdog w = running(t);
    run(w, t, 2000, never, POWER_ON);
    CHECK(run(w, t, FRAME, always, POWER_OFF) == KHR_WDG_OK, "state=%d", w.state);
    CHECK(run(w, t, 5000, always, POWER_ON) == KHR_WDG_OK, "state=%d", w.state);
  }

  std::printf("[7] LIMP 中に Power OFF でも、パケットが届かなければ解けない\n");
  {
    uint32_t t = 0;
    KhrWatchdog w = running(t);
    run(w, t, 2000, never, POWER_ON);
    // fresh=false なら all_power_off は呼び出し側で false になるが、念のため true を渡しても解けないこと
    for (int i = 0; i < 100; i++, t += FRAME) w.update(t, false, true);
    CHECK(w.state == KHR_WDG_LIMP, "state=%d", w.state);
  }

  std::printf("[8] パケット間隔が 190 ms（Wi-Fi の揺らぎ）なら HOLD に入らない\n");
  {
    uint32_t t = 0;
    KhrWatchdog w = running(t);
    bool left_ok = false;
    for (uint32_t k = 0; k < 600; k++, t += FRAME) {
      const bool fresh = (k % 19) == 0; // 190 ms ごと
      if (w.update(t, fresh, false) != KHR_WDG_OK) left_ok = true;
    }
    CHECK(!left_ok, "190 ms 間隔で OK 以外になった");
  }

  std::printf("[9] ループが 2 秒止まった（1 回の update で途絶 2 s）ら直接 LIMP\n");
  {
    uint32_t t = 0;
    KhrWatchdog w = running(t);
    t += 2000;
    CHECK(w.update(t, false, false) == KHR_WDG_LIMP, "state=%d", w.state);
  }

  std::printf("[10] millis() の桁あふれ（49.7 日）をまたいでも時間を正しく測る\n");
  {
    KhrWatchdog w(TIMEOUT, HOLD);
    uint32_t t = 0xFFFFFFFFu - 500u + 1u; // 桁あふれの 500 ms 前
    t -= t % FRAME;
    run(w, t, 400, always, POWER_OFF); // 桁あふれの直前までパケット
    run(w, t, 300, always, POWER_ON);  // 桁あふれをまたいでパケット
    CHECK(w.state == KHR_WDG_OK, "state=%d", w.state);
    CHECK(run(w, t, 190, never, POWER_ON) == KHR_WDG_OK, "state=%d", w.state);
    CHECK(run(w, t, 20, never, POWER_ON) == KHR_WDG_HOLD, "state=%d", w.state);
  }

  std::printf("[11] ありえない状態値になったら LIMP（安全側）\n");
  {
    KhrWatchdog w(TIMEOUT, HOLD);
    w.state = 7;
    CHECK(w.update(0, true, false) == KHR_WDG_LIMP, "state=%d", w.state);
  }

  std::printf("[12] 状態語のビット割り当て（PC 側 khr_common/gravity.py の selftest と同じ値で突き合わせる）\n");
  {
    // LIMP・重力あり・監視有効・加速度 2・システム 3（CALIB_STAT = sys3<<6 | gyro1<<4 | accel2<<2 | mag0）
    const uint8_t calib = (3 << 6) | (1 << 4) | (2 << 2) | 0;
    CHECK(khr_pack_status(KHR_WDG_LIMP, true, true, calib) == 0x6BEF, "0x%04X",
          khr_pack_status(KHR_WDG_LIMP, true, true, calib));
    CHECK(khr_pack_status(KHR_WDG_OK, false, true, 0) == 0x6B09, "0x%04X", khr_pack_status(KHR_WDG_OK, false, true, 0));
    // int16 として送っても正の値（上位 bit が立たない）
    CHECK((int16_t)khr_pack_status(KHR_WDG_LIMP, true, true, 0xFF) > 0, "負になった");
  }

  if (g_fail) {
    std::printf("FAILED: %d 件\n", g_fail);
    return EXIT_FAILURE;
  }
  std::printf("ALL PASSED\n");
  return EXIT_SUCCESS;
}
