
---

## Dual Vision Pipeline Architecture

The predictive crop row tracking system utilizes a multi-layered computer vision framework designed to maintain temporal and spatial continuity during field operations. The system operates by fusing inputs from two distinct visual tracking methodologies: deep-learning-based object detection via YOLO and classical color-space segmentation via OpenCV green color masking.

```text
+----------------------+----------------------------------+----------------------------------+-----------------------------------+
| PIPELINE COMPONENT   | PRIMARY DETECTION TARGET         | PROCESSING OUTPUT                | FALLBACK PRIORITY                 |
+----------------------+----------------------------------+----------------------------------+-----------------------------------+
| YOLO Engine          | Object bounding boxes around     | Geometric center coordinates     | Primary tracking source           |
|                      | crop rows                        | (x_YOLO, y_YOLO)                 |                                   |
+----------------------+----------------------------------+----------------------------------+-----------------------------------+
| OpenCV Engine        | Green color space blob           | Geometric center coordinates     | Secondary tracking source         |
|                      | segmentation                     | (x_Green, y_Green)               |                                   |
+----------------------+----------------------------------+----------------------------------+-----------------------------------+
| Purple Square Target | Spatial fusion of YOLO and       | Unified spatial target           | Consolidated tracking reference   |
|                      | OpenCV centers                   | coordinate                       |                                   |
+----------------------+----------------------------------+----------------------------------+-----------------------------------+

```

### Spatial Coordinate Extraction and Thresholding

* **Bounding Box Calculation:** The YOLO object detection module identifies crop rows within incoming video frames and generates bounding boxes surrounding each detected row segment. The geometric center of each bounding box is extracted to establish a localized coordinate point.


* **Color Blob Segmentation:** Concurrently, the OpenCV image processing pipeline isolates green regions within the frame using color threshold masking. The geometric centroids of these green color blobs are computed to provide an independent spatial location.


* **Horizontal Threshold Alignment:** The camera frame is bisected by a designated horizontal threshold line corresponding to the frame's vertical midpoint (`mid_y`). As the camera traverses the crop field, spatial centers move across the frame.


* **Crossing Event Timestamping:** The system continuously monitors the vertical position of detected coordinates. The exact timestamp is logged the moment a geometric center crosses the `mid_y` threshold line.



---

## Sensor Fusion and Unified Target Calculation

To maintain reliable spatial tracking despite visual occlusions or varying ambient light, the system constructs a unified spatial target known as the "purple square". This target synthesizes spatial predictions from both visual processing streams.

```text
                  +-----------------------------------+
                  |   Frame Ingestion & Processing    |
                  +-----------------+-----------------+
                                    |
                  +-----------------+-----------------+
                  |  YOLO Bounding  |  OpenCV Green   |
                  |  Box Center     |  Blob Center    |
                  +--------+--------+--------+--------+
                           |                 |
                           +--------+--------+
                                    |
                 +------------------v------------------+
                 | Spatial Proximity Check (<= 100px)? |
                 +--------+-------------------+--------+
                          |                   |
                 YES      |                   | NO / FAIL
                          v                   v
      +-------------------+---+     +---------+---------+
      | Weighted Fusion:      |     | Evaluate Sensor   |
      | 70% YOLO / 30% Green  |     | Fallback State    |
      +-------------------+---+     +---------+---------+
                          |                   |
                          |         +---------+---------+
                          |         | 1. YOLO Center    |
                          |         | 2. Green Center   |
                          |         +---------+---------+
                          |                   |
                          +--------+----------+
                                   |
                                   v
                      +------------+------------+
                      |  Unified Tracking Target|
                      |    ("Purple Square")    |
                      +-------------------------+

```

### Spatial Weighting and Fallback Hierarchy

* **Proximity Evaluation:** The spatial distance between the YOLO bounding box center and the OpenCV green blob center is evaluated.


* **Dual-Sensor Fusion:** When both detection streams identify centers within a 100-pixel proximity threshold, the system computes a weighted moving average location. The position of the unified "purple square" target is calculated using a 70% weighting assigned to the YOLO center and a 30% weighting assigned to the OpenCV green center:



$$\text{Target}\_{\text{center}} = 0.70 \cdot \text{Center}\_{\text{YOLO}} + 0.30 \cdot \text{Center}\_{\text{Green}}$$

* **Primary Fallback Protocol:** If the OpenCV green blob detection fails due to uneven lighting, weed interference, or improper color thresholding, the system transitions to its primary fallback state. Under this condition, the tracking target relies strictly on the YOLO bounding box center.


* **Secondary Fallback Protocol:** If the YOLO object detection network fails to output a bounding box due to occlusion or inference drops, the system defaults to its secondary fallback state. In this mode, the system uses the OpenCV green blob center as a final resort.



---

## Detection Merging and Event Validation

Crossing events detected by individual vision streams must undergo temporal validation before being logged as official field triggers.

```text
 +-----------------------------------------------------------------------+
 |                    Crossing Timestamp Detection                       |
 |    YOLO Timestamp (t_YOLO)  |  OpenCV Green Timestamp (t_Green)      |
 +-----------------------------------+-----------------------------------+
                                     |
                                     v
         +---------------------------+---------------------------+
         | Is |t_YOLO - t_Green| <= (expected_time_delta / 3)?   |
         +---------------------------+---------------------------+
                                     |
                    +----------------+----------------+
                    |                                 |
                 YES|                                 |NO
                    v                                 v
 +------------------+------------------+    +---------+----------+
 | Merge Time Deltas into              |    | Reject Dual-Merge  |
 | AVERAGED_TIME_DELTA_ARRAY           |    | Process Individual |
 +------------------+------------------+    | Stream Signals     |
                    |                       +--------------------+
                    v
 +------------------+------------------+
 | Trigger Valid "Yellow Flash" Event |
 +-------------------------------------+

```

### Temporal Window Verification

* **Delta Window Calculation:** The system defines a dynamic temporal acceptance window based on historical row spacing. This window threshold is set to one-third of the expected time interval between rows:



$$\text{Window}\_{\text{max}} = \frac{\text{expectedtimedelta}}{3}$$

* **Timestamp Comparison:** When a YOLO crossing timestamp $t_{\text{YOLO}}$ and an OpenCV green crossing timestamp $t_{\text{Green}}$ occur, the absolute time difference between them is measured.


* **Array Merging:** If $\vert{}t_{\text{YOLO}} - t_{\text{Green}}\vert{} \le \text{Window}_{\text{max}}$, the crossings are validated as representing the same physical crop row. The time deltas are merged into the system's `AVERAGED_TIME_DELTA_ARRAY`.


* **Event Triggering:** The successful registration of a merged timestamp entry in `AVERAGED_TIME_DELTA_ARRAY` officially fires a valid "Yellow Flash" event.



---

## Predictive Time Delta Modeling

To project when the next crop row will cross the threshold, the system processes historical crossing intervals through a weighted moving average model.

### Historical Data Arrays

* `LIGHT_BULB_FLASH_DELTA_ARRAY`: Stores the actual elapsed time intervals measured between consecutive validated "Yellow Flash" events.


* `AVERAGED_TIME_DELTA_ARRAY`: Stores merged timestamp values derived from combined YOLO and OpenCV detection events.


* `PREDICTED_TIME_DELTA_ARRAY`: Stores calculated target timestamps for upcoming predicted row crossings.



### Weighted Moving Average Formula

When at least 5 historical flash events have been recorded in `LIGHT_BULB_FLASH_DELTA_ARRAY`, the system calculates `expected_time_delta` for the next row. The calculation applies descending weights across the 5 most recent temporal deltas, prioritizing recent field velocity over older observations:

$$\text{expectedtimedelta} = 0.30(\Delta t_{-1}) + 0.25(\Delta t_{-2}) + 0.20(\Delta t_{-3}) + 0.15(\Delta t_{-4}) + 0.10(\Delta t_{-5})$$

Where:

* $\Delta t_{-1}$ represents the most recent elapsed flash delta.


* $\Delta t_{-5}$ represents the oldest elapsed flash delta in the 5-point evaluation window.



### Projection Registration

Once `expected_time_delta` is computed, the exact timestamp for the next predicted flash event is projected:

$$\text{Timestamp}_{\text{predicted}} = t_{\text{current}} + \text{expectedtimedelta}$$

This calculated value is appended to `PREDICTED_TIME_DELTA_ARRAY` to dictate downstream control timing.

---

## Edge Case Handling and System Robustness

Operating in real-world agricultural fields exposes visual tracking systems to missing plants, hardware inference delays, and warm-up state variations. The control algorithm incorporates several recovery routines to handle these edge cases.

### Mathematical Interpolation of Missed Rows

When physical gaps occur in a crop row or vision sensors fail to detect a plant, the time interval between consecutive detections spikes. Uncorrected, this large time delta would distort the moving average model. The dedicated function `append_smoothed_crossing` handles these large gaps.

```text
                +---------------------------------------+
                |    Measure Observed Time Delta (dt)   |
                +-------------------+-------------------+
                                    |
                                    v
            +-----------------------+-----------------------+
            | Evaluate Ratio R = dt / expected_time_delta   |
            +-----------------------+-----------------------+
                                    |
         +--------------------------+--------------------------+
         |                          |                          |
   R approx 2.0               R approx 3.0               R approx 4.0
         |                          |                          |
         v                          v                          v
+--------+--------+        +--------+--------+        +--------+--------+
| Divide dt by 2.0|        | Divide dt by 3.0|        | Divide dt by 4.0|
| Synthesize 1    |        | Synthesize 2    |        | Synthesize 3    |
| Missing Crossing|        | Missing Crossings|       | Missing Crossings|
+--------+--------+        +--------+--------+        +--------+--------+
         |                          |                          |
         +--------------------------+--------------------------+
                                    |
                                    v
                +-------------------+-------------------+
                | Append Synthetic Data to Restore      |
                | Sequence Stability & Delta Array      |
                +---------------------------------------+

```

* **Anomaly Detection:** The observed time delta $\Delta t_{\text{observed}}$ is compared against `expected_time_delta`. The system calculates ratio $R = \frac{\Delta t_{\text{observed}}}{\text{expectedtimedelta}}$.


* **Double Gap ($R \approx 2.0$):** If the observed delta is approximately twice the expected interval, the system determines that exactly one crop row was missed. The function divides $\Delta t_{\text{observed}}$ by $2.0$ and inserts the synthesized interval to preserve continuity.


* **Triple Gap ($R \approx 3.0$):** If the observed delta is approximately three times the expected interval, the system determines that two consecutive crop rows were missed. The function divides $\Delta t_{\text{observed}}$ by $3.0$ and appends synthesized intervals.


* **Quadruple Gap ($R \approx 4.0$):** If the observed delta is approximately four times the expected interval, the system divides $\Delta t_{\text{observed}}$ by $4.0$ to reconstruct the missing data points.



### Dynamic Weighting during Cold Start

During initial vehicle movement, fewer than 5 flash events are available in `LIGHT_BULB_FLASH_DELTA_ARRAY`. To prevent calculation errors or array out-of-bounds exceptions, the system dynamically reallocates weighting fractions.

```text
  +-------------------------------------------------------------------+
  |               Check Size of LIGHT_BULB_FLASH_DELTA_ARRAY           |
  +---------------------------------+---------------------------------+
                                    |
            +-----------------------+-----------------------+
            |                                               |
     History < 5 Points                             History >= 5 Points
            |                                               |
            v                                               v
+-----------+-----------+                       +-----------+-----------+
| Reallocate Weights    |                       | Standard WMA Weights: |
| e.g., 3-Point Mode:   |                       | 30%, 25%, 20%, 15%, 10%|
| 60%, 30%, 10%         |                       +-----------------------+
+-----------+-----------+
            |
            v
+-----------+-----------------------------------------------------------+
| Calculate expected_time_delta using available points without errors  |
+-----------------------------------------------------------------------+

```

* **Dynamic Array Scaling:** The script inspects the length of `LIGHT_BULB_FLASH_DELTA_ARRAY` prior to executing the moving average function.


* **Three-Point Re-allocation:** If only 3 flash events are logged in memory, the weighting vector adjusts to assign 60% weight to the most recent entry, 30% to the second, and 10% to the third:



$$\text{expectedtimedelta}_{\text{3-point}} = 0.60(\Delta t_{-1}) + 0.30(\Delta t_{-2}) + 0.10(\Delta t_{-3})$$

* **Scale-Up Sequence:** As new crossing events are validated, the system incrementally expands the weighting array until reaching the full 5-point distribution.



### Inference Jitter Deduplication

High-frequency processing jitter in object detection can occasionally generate duplicate crossing triggers within rapid succession.

* **Scanning Sweep:** A dedicated filtering loop continuously scans `AVERAGED_TIME_DELTA_ARRAY`.


* **Duplicate Elimination:** When consecutive timestamps fall below a minimum physical threshold caused by frame-rate stutter or bounding box flicker, the loop purges the duplicate entries. This cleanup step prevents false double-counting within downstream prediction models.



---

## Full End-to-End Control Routine Trace

```text
 +------------------------------------------------------------------------+
 | Step 1: Ingest Camera Frame & Extract YOLO / OpenCV Centers            |
 +-----------------------------------+------------------------------------+
                                     |
                                     v
 +-----------------------------------+------------------------------------+
 | Step 2: Track Spatial Position Relative to mid_y Threshold             |
 +-----------------------------------+------------------------------------+
                                     |
                                     v
 +-----------------------------------+------------------------------------+
 | Step 3: Compute Unified "Purple Square" Target & Fallback States       |
 +-----------------------------------+------------------------------------+
                                     |
                                     v
 +-----------------------------------+------------------------------------+
 | Step 4: Validate Crossings within Temporal Window (expected_delta / 3) |
 +-----------------------------------+------------------------------------+
                                     |
                                     v
 +-----------------------------------+------------------------------------+
 | Step 5: Merge Valid Events into AVERAGED_TIME_DELTA_ARRAY              |
 +-----------------------------------+------------------------------------+
                                     |
                                     v
 +-----------------------------------+------------------------------------+
 | Step 6: Perform Deduplication Sweep to Remove Jitter Spikes            |
 +-----------------------------------+------------------------------------+
                                     |
                                     v
 +-----------------------------------+------------------------------------+
 | Step 7: Check Gap Spikes via append_smoothed_crossing (2x, 3x, 4x)     |
 +-----------------------------------+------------------------------------+
                                     |
                                     v
 +-----------------------------------+------------------------------------+
 | Step 8: Update LIGHT_BULB_FLASH_DELTA_ARRAY History                    |
 +-----------------------------------+------------------------------------+
                                     |
                                     v
 +-----------------------------------+------------------------------------+
 | Step 9: Compute WMA expected_time_delta (Dynamic or 5-Point)           |
 +-----------------------------------+------------------------------------+
                                     |
                                     v
 +-----------------------------------+------------------------------------+
 | Step 10: Append Future Timestamp to PREDICTED_TIME_DELTA_ARRAY         |
 +------------------------------------------------------------------------+

```

1. **Frame Capture and Detection:** Image frames are processed simultaneously by the YOLO neural network and OpenCV green masking routines.


2. **Coordinate Localization:** Bounding box centers and green blob centroids are extracted and tracked relative to frame coordinate space.


3. **Target Spatial Synthesis:** Distance between centers is checked against the 100-pixel threshold. The system generates the unified target coordinate using the 70/30 weighted formula or selects appropriate fallback modes.


4. **Midpoint Crossing Detection:** The system registers timestamps when target coordinates intersect the vertical midpoint `mid_y` threshold line.


5. **Temporal Windowing:** Dual crossings occurring within $\frac{\text{expectedtimedelta}}{3}$ are merged into `AVERAGED_TIME_DELTA_ARRAY` and trigger a "Yellow Flash" event.


6. **Jitter Scrubbing:** The array filtering loop scans for temporal spikes caused by frame inference delays and purges duplicate entries.


7. **Interpolation Check:** `append_smoothed_crossing` evaluates interval sizes. Large gaps matching $2.0\times$, $3.0\times$, or $4.0\times$ expected thresholds are mathematically divided to synthesize missing row events.


8. **History Array Maintenance:** Validated and interpolated time deltas are logged into `LIGHT_BULB_FLASH_DELTA_ARRAY`.


9. **Moving Average Calculation:** Historical entries are evaluated through the 5-point weighted moving average model (or dynamic reduced-point models during cold starts) to establish `expected_time_delta`.


10. **Target Projection:** The calculated `expected_time_delta` is added to the current time, registering the projected event timestamp inside `PREDICTED_TIME_DELTA_ARRAY`.
