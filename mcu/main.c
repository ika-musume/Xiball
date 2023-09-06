/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2023 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "usb_device.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdio.h>
#include <math.h>
#include "usbd_cdc_if.h"

TIM_HandleTypeDef htim2;

/* USER CODE BEGIN PV */
extern uint8_t UserRxBufferFS[APP_RX_DATA_SIZE];
extern uint8_t UserTxBufferFS[APP_TX_DATA_SIZE];
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_TIM2_Init(void);


int getPulseWidth(int direction, float angle, int pw0d, int pw10d, int pw20d, int pw30d, int pw40d, int pw50d, int pw60d, int pw70d, int pw80d, int pw90d) {
    //direction -1 = reverse 2400(0 deg) -> 1500(90 deg)
    //direction 1 = forward 650(0 deg) -> 1500(90 deg)
         
         if(angle < 0 ) return pw0d;
    else if(angle < 10) return (int)round((float)pw0d  + ((((float)abs(pw0d -pw10d))/1000) * ((angle-0 )*100) * (float)direction));
    else if(angle < 20) return (int)round((float)pw10d + ((((float)abs(pw10d-pw20d))/1000) * ((angle-10)*100) * (float)direction));
    else if(angle < 30) return (int)round((float)pw20d + ((((float)abs(pw20d-pw30d))/1000) * ((angle-20)*100) * (float)direction));
    else if(angle < 40) return (int)round((float)pw30d + ((((float)abs(pw30d-pw40d))/1000) * ((angle-30)*100) * (float)direction));
    else if(angle < 50) return (int)round((float)pw40d + ((((float)abs(pw40d-pw50d))/1000) * ((angle-40)*100) * (float)direction));
    else if(angle < 60) return (int)round((float)pw50d + ((((float)abs(pw50d-pw60d))/1000) * ((angle-50)*100) * (float)direction));
    else if(angle < 70) return (int)round((float)pw60d + ((((float)abs(pw60d-pw70d))/1000) * ((angle-60)*100) * (float)direction));
    else if(angle < 80) return (int)round((float)pw70d + ((((float)abs(pw70d-pw80d))/1000) * ((angle-70)*100) * (float)direction));
    else if(angle < 90) return (int)round((float)pw80d + ((((float)abs(pw80d-pw90d))/1000) * ((angle-80)*100) * (float)direction));
    else                return pw90d;
}


int main(void) {
    HAL_Init();

    SystemClock_Config();

    MX_USB_DEVICE_Init();
    MX_GPIO_Init();
    MX_TIM2_Init();

    //84,000kHz / 84 = 1000kHz
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_2);
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_3);

    htim2.Instance -> ARR = 20000;
    htim2.Instance -> CCR1 = 20000 - 1500; //high time period -> inverted by 2SC1815 -> low time period(/1000 ms)
    htim2.Instance -> CCR2 = 20000 - 1500; //1500 is the neutral position
    htim2.Instance -> CCR3 = 20000 - 1500;

    int reqDegServoA, reqDegServoB, reqDegServoC;
    int servoA_PW, servoB_PW, servoC_PW;
    int servoPW;

    while (1) {
        uint16_t len = strlen((const char*)UserRxBufferFS); //check received string's length
        if(len > 0) {
            //Echo
            strncpy((char *)UserTxBufferFS, (const char*)UserRxBufferFS, len);
            strcat((char *)UserTxBufferFS, "\r\n");

            //reverse(MG996R)
            if(UserRxBufferFS[0] == 0x72) {
                reqDegServoA = ((int)(UserRxBufferFS[1] - 48) * 1000) +
                		       ((int)(UserRxBufferFS[2] - 48) * 100) + 
                               ((int)(UserRxBufferFS[3] - 48) * 10) +
                               ((int)(UserRxBufferFS[4] - 48) * 1);
                reqDegServoB = ((int)(UserRxBufferFS[5] - 48) * 1000) + 
                               ((int)(UserRxBufferFS[6] - 48) * 100) + 
                               ((int)(UserRxBufferFS[7] - 48) * 10);
                               ((int)(UserRxBufferFS[8] - 48) * 1);
                reqDegServoC = ((int)(UserRxBufferFS[9] - 48) * 1000) + 
                               ((int)(UserRxBufferFS[10] - 48) * 100) + 
                               ((int)(UserRxBufferFS[11] - 48) * 10);
                               ((int)(UserRxBufferFS[12] - 48) * 1);

                servoA_PW = getPulseWidth(-1, ((float)reqDegServoA/100), 2400, 2310, 2228, 2130, 2025, 1935, 1840, 1740, 1640, 1535);
                servoB_PW = getPulseWidth(-1, ((float)reqDegServoB/100), 2410, 2330, 2234, 2150, 2052, 1978, 1865, 1770, 1650, 1565);
                servoC_PW = getPulseWidth(-1, ((float)reqDegServoC/100), 2410, 2320, 2220, 2140, 2040, 1960, 1860, 1755, 1640, 1515);

                htim2.Instance -> CCR1 = 20000 - servoA_PW;
                htim2.Instance -> CCR2 = 20000 - servoB_PW;
                htim2.Instance -> CCR3 = 20000 - servoC_PW;
            }

            //forward(HS-311)
            else if(UserRxBufferFS[0] == 0x66) {
                reqDegServoA = ((int)(UserRxBufferFS[1] - 48) * 1000) +
                		       ((int)(UserRxBufferFS[2] - 48) * 100) + 
                               ((int)(UserRxBufferFS[3] - 48) * 10) +
                               ((int)(UserRxBufferFS[4] - 48) * 1);
                reqDegServoB = ((int)(UserRxBufferFS[5] - 48) * 1000) + 
                               ((int)(UserRxBufferFS[6] - 48) * 100) + 
                               ((int)(UserRxBufferFS[7] - 48) * 10);
                               ((int)(UserRxBufferFS[8] - 48) * 1);
                reqDegServoC = ((int)(UserRxBufferFS[9] - 48) * 1000) + 
                               ((int)(UserRxBufferFS[10] - 48) * 100) + 
                               ((int)(UserRxBufferFS[11] - 48) * 10);
                               ((int)(UserRxBufferFS[12] - 48) * 1);

                servoA_PW = getPulseWidth(1, ((float)reqDegServoA/100), 650, 760, 860, 960, 1055, 1150, 1240, 1330, 1420, 1510);
                servoB_PW = getPulseWidth(1, ((float)reqDegServoB/100), 665, 765, 865, 965, 1060, 1150, 1245, 1340, 1430, 1525);
                servoC_PW = getPulseWidth(1, ((float)reqDegServoC/100), 645, 745, 845, 945, 1040, 1130, 1225, 1315, 1410, 1500);

                htim2.Instance -> CCR1 = 20000 - servoA_PW;
                htim2.Instance -> CCR2 = 20000 - servoB_PW;
                htim2.Instance -> CCR3 = 20000 - servoC_PW;
            }

            //Motor A control
            else if(UserRxBufferFS[0] == 0x61) {
                servoPW = ((int)(UserRxBufferFS[1] - 48) * 1000) + ((int)(UserRxBufferFS[2] - 48) * 100) + ((int)(UserRxBufferFS[3] - 48) * 10) + ((int)(UserRxBufferFS[4] - 48) * 1);
                htim2.Instance -> CCR1 = 20000 - servoPW;
            }

            //Motor B control
            else if(UserRxBufferFS[0] == 0x62) {
                servoPW = ((int)(UserRxBufferFS[1] - 48) * 1000) + ((int)(UserRxBufferFS[2] - 48) * 100) + ((int)(UserRxBufferFS[3] - 48) * 10) + ((int)(UserRxBufferFS[4] - 48) * 1);
                htim2.Instance -> CCR2 = 20000 - servoPW;
            }

            //Motor C control
            else if(UserRxBufferFS[0] == 0x63) {
                servoPW = ((int)(UserRxBufferFS[1] - 48) * 1000) + ((int)(UserRxBufferFS[2] - 48) * 100) + ((int)(UserRxBufferFS[3] - 48) * 10) + ((int)(UserRxBufferFS[4] - 48) * 1);
                htim2.Instance -> CCR3 = 20000 - servoPW;
            }
            else {
              CDC_Transmit_FS((uint8_t*)UserTxBufferFS, len);
            }
            memset(UserRxBufferFS, 0, sizeof(UserRxBufferFS));
            memset(UserTxBufferFS, 0, sizeof(UserTxBufferFS));
          }
    }
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE2);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM = 25;
  RCC_OscInitStruct.PLL.PLLN = 336;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV4;
  RCC_OscInitStruct.PLL.PLLQ = 7;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief TIM2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM2_Init(void)
{

  /* USER CODE BEGIN TIM2_Init 0 */

  /* USER CODE END TIM2_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_OC_InitTypeDef sConfigOC = {0};

  /* USER CODE BEGIN TIM2_Init 1 */

  /* USER CODE END TIM2_Init 1 */
  htim2.Instance = TIM2;
  htim2.Init.Prescaler = 84;
  htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim2.Init.Period = 20000;
  htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_Base_Init(&htim2) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim2, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_Init(&htim2) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim2, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 0;
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  if (HAL_TIM_PWM_ConfigChannel(&htim2, &sConfigOC, TIM_CHANNEL_1) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_ConfigChannel(&htim2, &sConfigOC, TIM_CHANNEL_2) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_ConfigChannel(&htim2, &sConfigOC, TIM_CHANNEL_3) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM2_Init 2 */

  /* USER CODE END TIM2_Init 2 */
  HAL_TIM_MspPostInit(&htim2);

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
/* USER CODE BEGIN MX_GPIO_Init_1 */
/* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOH_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();

/* USER CODE BEGIN MX_GPIO_Init_2 */
/* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {

  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
