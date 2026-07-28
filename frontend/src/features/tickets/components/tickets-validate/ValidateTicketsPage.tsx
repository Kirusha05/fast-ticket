import { useState, useEffect, useRef, useCallback } from "react";
import { useValidateTicket } from "../../hooks/useValidateTicket";
import { Html5Qrcode } from "html5-qrcode";
import { Button, Input, Card, CardContent, Badge } from "@/components/ui";
import {
  CheckCircle2,
  XCircle,
  Camera,
  CameraOff,
  ScanLine,
  Loader2,
} from "lucide-react";

type ScanStatus = "idle" | "VALID" | "INVALID" | "ERROR";

interface ScanResult {
  status: ScanStatus;
  message: string;
}

const STATUS_STYLES: Record<
  Exclude<ScanStatus, "idle">,
  { bg: string; icon: typeof CheckCircle2 }
> = {
  VALID: { bg: "bg-emerald-600", icon: CheckCircle2 },
  INVALID: { bg: "bg-red-600", icon: XCircle },
  ERROR: { bg: "bg-red-600", icon: XCircle },
};

const SCAN_COOLDOWN_MS = 2000;

export const ValidateTicketsPage = () => {
  const { mutate, isPending } = useValidateTicket();

  const [isScanning, setIsScanning] = useState(false);
  const [scanResult, setScanResult] = useState<ScanResult>({
    status: "idle",
    message: "",
  });
  const [manualId, setManualId] = useState("");

  // using refs for instantly mutable variables that don't trigger re-renders (better than variables outside the component)
  const scannerRef = useRef<Html5Qrcode | null>(null);
  const scannerRunning = useRef(false);
  const isLockedRef = useRef(false);
  const cooldownTimeoutRef = useRef<number | null>(null);

  const scannerConfig = {
    fps: 10,
    qrbox: { width: 250, height: 250 },
    aspectRatio: 1.333,
  };

  const clearCooldownTimer = () => {
    if (cooldownTimeoutRef.current !== null) {
      window.clearTimeout(cooldownTimeoutRef.current);
      cooldownTimeoutRef.current = null;
    }
  };

  const stopScanner = useCallback(async () => {
    if (!scannerRef.current || !scannerRunning.current) return;

    try {
      await scannerRef.current.stop();
    } catch (err) {
      console.error("Failed to stop scanner", err);
    } finally {
      scannerRunning.current = false;
      setIsScanning(false);
    }
  }, []);

  const startScanner = useCallback(async () => {
    if (scannerRunning.current || isLockedRef.current) return;

    if (!scannerRef.current) {
      scannerRef.current = new Html5Qrcode("qr-reader-container");
    }

    try {
      await scannerRef.current.start(
        { facingMode: "environment" },
        scannerConfig,
        // successful scan callback
        async (decodedText: string) => {
          // lock immediately so the same QR cannot trigger again
          if (isLockedRef.current) return;
          isLockedRef.current = true;

          mutate(
            { ticket_id: decodedText },
            {
              onSuccess: () => {
                setScanResult({
                  status: "VALID",
                  message: "Ticket valid",
                });
                if (navigator.vibrate) navigator.vibrate(200);
              },
              onError: (err) => {
                setScanResult({
                  status: "INVALID",
                  message: err.message,
                });
                if (navigator.vibrate) navigator.vibrate([300, 100, 300]);
              },
              onSettled: () => {
                cooldownTimeoutRef.current = window.setTimeout(async () => {
                  setScanResult({ status: "idle", message: "" });
                  isLockedRef.current = false;
                }, SCAN_COOLDOWN_MS);
              },
            },
          );
        },
        // error scan callback, currently just ignoring the errors
        () => {},
      );

      scannerRunning.current = true;
      setIsScanning(true);
    } catch (err) {
      console.error("Failed to start camera", err);
      isLockedRef.current = false;
      setScanResult({
        status: "ERROR",
        message: "Camera access denied. Check permissions.",
      });
    }
  }, [mutate, scannerConfig, stopScanner]);

  // unmount cleanup, stops the camera when user navigates away
  useEffect(() => {
    return () => {
      clearCooldownTimer();
      stopScanner();
    };
  }, [stopScanner]);

  const handleManualSubmit = (e: React.SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    const value = manualId.trim();
    if (!value) return;

    if (isLockedRef.current) return;
    isLockedRef.current = true;
    clearCooldownTimer();

    mutate(
      { ticket_id: value },
      {
        onSuccess: () => {
          setScanResult({
            status: "VALID",
            message: "Ticket valid",
          });
          if (navigator.vibrate) navigator.vibrate(200);
        },
        onError: (err) => {
          setScanResult({
            status: "INVALID",
            message: err.message,
          });
          if (navigator.vibrate) navigator.vibrate([300, 100, 300]);
        },
        onSettled: () => {
          cooldownTimeoutRef.current = window.setTimeout(async () => {
            setScanResult({ status: "idle", message: "" });
            isLockedRef.current = false;
          }, SCAN_COOLDOWN_MS);
        },
      },
    );

    setManualId("");
  };

  const resultStyle =
    scanResult.status !== "idle" ? STATUS_STYLES[scanResult.status] : null;
  const ResultIcon = resultStyle?.icon;

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Validate tickets
          </h1>
          <p className="text-sm text-muted-foreground">
            Scan a QR code or enter a ticket ID manually
          </p>
        </div>
        <Badge
          variant={isScanning ? "default" : "secondary"}
          className="gap-1.5"
        >
          <span
            className={`h-1.5 w-1.5 rounded-full ${
              isScanning
                ? "bg-emerald-400 animate-pulse"
                : "bg-muted-foreground"
            }`}
          />
          {isScanning ? "Scanning" : "Camera off"}
        </Badge>
      </div>

      <Card className="overflow-hidden border-border/60 py-0">
        <CardContent className="p-0">
          <div className="relative aspect-[3/4] md:aspect-[4/3] w-full bg-black">
            <div
              id="qr-reader-container"
              className="h-full w-full [&>video]:object-cover"
            />

            {!isScanning && scanResult.status === "idle" && (
              <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-black text-muted-foreground">
                <ScanLine className="h-10 w-10" strokeWidth={1.5} />
                <p className="text-sm">Camera is off</p>
              </div>
            )}

            {isPending && (
              <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-black text-white">
                <Loader2 className="h-8 w-8 animate-spin" />
                <p className="text-sm font-medium">Checking ticket…</p>
              </div>
            )}

            {scanResult.status !== "idle" && ResultIcon && (
              <div
                className={`absolute inset-0 flex flex-col items-center justify-center gap-3 text-white transition-colors ${resultStyle?.bg}`}
              >
                <ResultIcon className="h-16 w-16" strokeWidth={1.5} />
                <h2 className="text-xl font-semibold">{scanResult.message}</h2>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {!isScanning ? (
        <Button onClick={startScanner} size="lg" className="gap-2">
          <Camera className="h-4 w-4" />
          Start camera
        </Button>
      ) : (
        <Button
          onClick={stopScanner}
          size="lg"
          variant="secondary"
          className="gap-2"
        >
          <CameraOff className="h-4 w-4" />
          Stop camera
        </Button>
      )}

      <div className="flex flex-col gap-2">
        <p className="text-center text-sm text-muted-foreground">
          QR code damaged? Enter the ticket ID manually
        </p>
        <form onSubmit={handleManualSubmit} className="flex gap-2">
          <Input
            value={manualId}
            onChange={(e) => setManualId(e.target.value)}
            placeholder="Ticket ID"
            className="flex-1"
          />
          <Button type="submit" disabled={!manualId.trim() || isPending}>
            Check
          </Button>
        </form>
      </div>
    </div>
  );
};
