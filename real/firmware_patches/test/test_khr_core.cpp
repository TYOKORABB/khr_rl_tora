// khr_core.h（通信監視の状態機械と状態語）のホスト上の単体テスト。
// ファームのフレーム周期（10 ms）で時間を進め、パケットの到着パターンごとに状態遷移を確かめる。
//
//   g++ -std=c++17 -Wall -Wextra -Werror -I <パッチ適用後の src> test_khr_core.cpp -o test_khr_core && ./test_khr_core
//   （build_fw.sh --test が上を実行する）

#include "khr_core.h"

#include <cstdio>
#include <cstdlib>
#include <vector>

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

// main.h の mrd_seq_predict_num() と同じ（シーケンス番号の予想値: +1、59999 の次は 0）
static uint16_t mrd_seq_next(uint16_t a) { return a + 1 > 59999 ? 0 : a + 1; }

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

  std::printf("[13] 一括読み取りの位置はレジスタ番地どおり（加速度 0x08・ジャイロ 0x14・Euler 0x1A・重力 0x2E〜0x33）\n");
  {
    CHECK(KHR_BNO_OFS_GYR == 0x14 - KHR_BNO_BURST_ADDR, "ジャイロの位置 %d", KHR_BNO_OFS_GYR);
    CHECK(KHR_BNO_OFS_EUL == 0x1A - KHR_BNO_BURST_ADDR, "Euler の位置 %d", KHR_BNO_OFS_EUL);
    CHECK(KHR_BNO_OFS_GRV == 0x2E - KHR_BNO_BURST_ADDR, "重力の位置 %d", KHR_BNO_OFS_GRV);
    CHECK(KHR_BNO_BURST_LEN == 0x34 - KHR_BNO_BURST_ADDR, "長さ %d", KHR_BNO_BURST_LEN);
  }

  std::printf("[14] 一括読み取りの換算は Adafruit_BNO055::getVector() と同じ（リトルエンディアン・符号つき）\n");
  {
    uint8_t buf[KHR_BNO_BURST_LEN] = {0};
    auto put = [&](int ofs, int16_t x, int16_t y, int16_t z) {
      const int16_t v[3] = {x, y, z};
      for (int i = 0; i < 3; i++) {
        buf[ofs + 2 * i] = (uint8_t)((uint16_t)v[i] & 0xFF);
        buf[ofs + 2 * i + 1] = (uint8_t)((uint16_t)v[i] >> 8);
      }
    };
    put(KHR_BNO_OFS_ACC, 981, -12, 0);
    put(KHR_BNO_OFS_GYR, 16, -32, 1);
    put(KHR_BNO_OFS_EUL, 5759, -1440, 32767);
    put(KHR_BNO_OFS_GRV, -967, 59, -32768);
    buf[6] = 0x55;   // 地磁気（使わない）
    buf[24] = 0x77;  // クォータニオン（使わない）
    KhrImuSample s;
    khr_decode_bno_burst(buf, s);
    CHECK(s.acc[0] == 981 / 100.0 && s.acc[1] == -12 / 100.0 && s.acc[2] == 0.0, "acc %f %f %f", s.acc[0], s.acc[1], s.acc[2]);
    CHECK(s.gyr[0] == 1.0 && s.gyr[1] == -2.0 && s.gyr[2] == 0.0625, "gyr %f %f %f", s.gyr[0], s.gyr[1], s.gyr[2]);
    CHECK(s.eul[0] == 5759 / 16.0 && s.eul[1] == -90.0 && s.eul[2] == 32767 / 16.0, "eul %f %f %f", s.eul[0], s.eul[1], s.eul[2]);
    CHECK(s.grv[0] == -967 / 100.0 && s.grv[1] == 59 / 100.0 && s.grv[2] == -32768 / 100.0, "grv %f %f %f", s.grv[0], s.grv[1], s.grv[2]);
    CHECK(!khr_all_zero(buf, KHR_BNO_BURST_LEN), "全部 0 と判定された");
    uint8_t zero[KHR_BNO_BURST_LEN] = {0};
    CHECK(khr_all_zero(zero, KHR_BNO_BURST_LEN), "全部 0 を見逃した");
    zero[KHR_BNO_BURST_LEN - 1] = 0x80; // 最後の 1 バイトだけ 0 でない
    CHECK(!khr_all_zero(zero, KHR_BNO_BURST_LEN), "最後の 1 バイトだけ 0 でないのを全部 0 と判定した");
  }

  std::printf("[15] IMU の診断語（PC 側 khr_common/gravity.py の selftest と同じ値で突き合わせる）\n");
  {
    CHECK(khr_pack_imu_diag(257, KHR_IMU_FAIL_ZERO_GRAV, KHR_IMU_MODE_LEGACY) == 0x1F01, "0x%04X",
          khr_pack_imu_diag(257, KHR_IMU_FAIL_ZERO_GRAV, KHR_IMU_MODE_LEGACY));
    CHECK(khr_pack_imu_diag(3, KHR_IMU_FAIL_SHORT, KHR_IMU_MODE_BURST) == 0x0E03, "0x%04X",
          khr_pack_imu_diag(3, KHR_IMU_FAIL_SHORT, KHR_IMU_MODE_BURST));
    // 診断語が PC → ESP32 の切り替えの印（0x6B4C）と取り違えられないこと
    bool clash = false;
    for (uint32_t c = 0; c < 256; c++)
      for (uint8_t r = 0; r < 16; r++)
        for (uint8_t m = 0; m < 4; m++)
          if (khr_pack_imu_diag(c, r, m) == KHR_IMU_LEGACY_MAGIC) clash = true;
    CHECK(!clash, "診断語が 0x6B4C になりうる");
  }

  // ---- 受信バッファの読み捨て（khr-getup.4）----
  // 偽の受信バッファ: パケット（マスターコマンド, シーケンス番号, チェックサムを壊すか）の列
  struct Pkt {
    int16_t master, seq;
    bool broken;
  };
  auto make = [](const Pkt &p, int16_t *m) {
    for (int i = 0; i < KHR_MRDM_LEN; i++) m[i] = 0;
    m[0] = p.master;
    m[1] = p.seq;
    m[2] = (int16_t)(p.seq * 7); // 中身の印
    int sum = 0;
    for (int i = 0; i < KHR_MRDM_LEN - 1; i++) sum += m[i];
    m[KHR_MRDM_LEN - 1] = (int16_t)(~sum);
    if (p.broken) m[3] = 1; // チェックサムを壊す
  };
  struct Queue {
    std::vector<Pkt> q;
    size_t pos = 0;
  };
  auto run_drain = [&](Pkt cur_p, std::vector<Pkt> rest, int16_t *cur, uint16_t &prev, size_t &left, int max = KHR_DRAIN_MAX) {
    make(cur_p, cur);
    Queue Q{rest};
    auto recv = [&](int16_t *dst) {
      if (Q.pos >= Q.q.size()) return false;
      make(Q.q[Q.pos++], dst);
      return true;
    };
    const int n = khr_udp_drain(cur, recv, prev, max);
    left = Q.q.size() - Q.pos;
    return n;
  };
  const int16_t N = KHR_MRDM_LEN, SPECIAL = 10003; // 通常 / 特殊コマンド（トリム設定の開始）

  std::printf("[16] 溜まった通常パケットは読み捨て、最新だけ残す（1 つ前の番号を返す）\n");
  {
    int16_t cur[KHR_MRDM_LEN];
    uint16_t prev = 0xFFFF;
    size_t left;
    const int n = run_drain({N, 1, false}, {{N, 2, false}, {N, 3, false}, {N, 4, false}, {N, 5, false}}, cur, prev, left);
    CHECK(n == 4 && cur[1] == 5 && cur[2] == 35 && prev == 4 && left == 0, "n=%d seq=%d prev=%u left=%zu", n, cur[1], prev, left);
    CHECK(khr_cksm_ok(cur), "残したパケットのチェックサム");
    CHECK(mrd_seq_next(prev) == (uint16_t)cur[1], "1 つ前の番号 +1 が残した番号（[2-5] でスキップと数えない）");
  }

  std::printf("[17] 特殊コマンドは読み捨てない（来たらそれを残して止める。後ろは次のフレーム）\n");
  {
    int16_t cur[KHR_MRDM_LEN];
    uint16_t prev = 0;
    size_t left;
    int n = run_drain({N, 1, false}, {{N, 2, false}, {SPECIAL, 3, false}, {N, 4, false}}, cur, prev, left);
    CHECK(n == 2 && cur[0] == SPECIAL && cur[1] == 3 && prev == 2 && left == 1, "n=%d master=%d seq=%d prev=%u left=%zu", n, cur[0], cur[1], prev, left);
    prev = 77;
    n = run_drain({SPECIAL, 1, false}, {{N, 2, false}}, cur, prev, left); // いま持っているのが特殊コマンド
    CHECK(n == 0 && cur[0] == SPECIAL && cur[1] == 1 && prev == 77 && left == 1, "n=%d seq=%d prev=%u left=%zu", n, cur[1], prev, left);
    n = run_drain({0, 1, false}, {{N, 2, false}}, cur, prev, left); // マスターコマンド 0（全サーボ脱力）も特殊
    CHECK(n == 0 && cur[0] == 0 && left == 1, "全サーボ脱力のコマンドを読み捨てた n=%d", n);
  }

  std::printf("[18] チェックサムの合わないパケットは捨てる（その番号は飛びとして残る）・何も無ければ変えない・上限で止める\n");
  {
    int16_t cur[KHR_MRDM_LEN];
    uint16_t prev = 0;
    size_t left;
    int n = run_drain({N, 1, false}, {{N, 2, true}, {N, 3, false}}, cur, prev, left);
    CHECK(n == 1 && cur[1] == 3 && prev == 1 && left == 0, "n=%d seq=%d prev=%u", n, cur[1], prev);
    CHECK(mrd_seq_next(prev) != (uint16_t)cur[1], "壊れたパケットの分はスキップとして検出されるべき");
    prev = 55;
    n = run_drain({N, 9, false}, {}, cur, prev, left);
    CHECK(n == 0 && cur[1] == 9 && prev == 55, "空の受信バッファで変わった n=%d", n);
    std::vector<Pkt> many;
    for (int16_t s = 2; s < 40; s++) many.push_back({N, s, false});
    n = run_drain({N, 1, false}, many, cur, prev, left);
    CHECK(n == KHR_DRAIN_MAX && left == many.size() - KHR_DRAIN_MAX, "上限 n=%d left=%zu", n, left);
  }

  if (g_fail) {
    std::printf("FAILED: %d 件\n", g_fail);
    return EXIT_FAILURE;
  }
  std::printf("ALL PASSED\n");
  return EXIT_SUCCESS;
}
