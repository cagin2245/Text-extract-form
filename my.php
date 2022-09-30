<?php 


function textractToTable($pureArr) {

		$num    = count($pureArr);
		$tables = array();
		$forms  = array();
		$i      = 0;
		$retArr = array();
        
		if($num > 0)
		{
            
			foreach($pureArr as $pp)
			{
               foreach($pp['ExpenseDocuments'] as $p )
               { 
				if(isset($p['SummaryFields']))
				{                    
					foreach($p['SummaryFields'] as $sfk => $sfv)
					{
						$i++;
						foreach($sfv as $kf => $val)
						{
							switch($kf)
							{
								case "Type":
									$forms[$i]['type'] = array(
										"Type"  		=> $val['Text'],
										"Confidence"    => $val['Confidence'],
									);
								break;

								case "ValueDetection":
									$forms[$i]['value'] = array(
										"value"  		=> isset($val['Text']) ? $val['Text'] : null ,
										"Confidence"    => isset($val['Confidence']) ? $val['Confidence'] : null ,
									);
								break;
								
								case "LabelDetection":
									$forms[$i]['label'] = array(
										"value"  		=> isset($val['Text']) ? $val['Text'] : null ,
										"Confidence"    => isset($val['Confidence']) ? $val['Confidence'] : null ,
									);
								break;
							}						
						}
					}
				}
				if(isset($p['LineItemGroups']))
				{
					foreach($p['LineItemGroups'] as $ltgk => $ltgv)
					{
						$tableIndex = $ltgv['LineItemGroupIndex'];		
						$trnum 		= 0;				
						foreach( $ltgv['LineItems'] as $tr)// her bir satır
						{
							
							$trnum++;
							foreach($tr['LineItemExpenseFields'] as $trk => $trv)
							{			
								print_r($trv);
								//getpre($trv['Type'])	;	
	
								if($trv['Type']['Text'] == "EXPENSE_ROW")
								{
									$tables[$tableIndex]['header']["EXPENSE_ROW"] = "EXPENSE_ROW" ;
								}
								foreach($trv as $k => $v)
								{					
									if($trnum == 1)// header
									{
										switch($k)
										{
											case "LabelDetection":
												$val = isset($v['Text']) ? $v['Text'] : null ; 
												
												$val = trim(preg_replace('/\([^)]+\)/', '', $val));
												
												$tables[$tableIndex]['header'][$trk] = $val ;
												
											break;										
										}
									}
									switch($k)
									{	
										case "ValueDetection":
											
											
											if(isset($tables[$tableIndex]['header'][$trk]))
											{
												
												$tables[$tableIndex]['body'][$tables[$tableIndex]['header'][$trk]][] = isset($v['Text']) ? $v['Text'] : null ;
												
											}	
										break;										
									}
								}
								if($trv['Type']['Text'] == "EXPENSE_ROW")
								{
									$tables[$tableIndex]['body'][$tables[$tableIndex]['header']['EXPENSE_ROW']][] = $trv['ValueDetection']['Text'] ;
									
									
								}
							}
						}
					}
				}
			}
        }
		}
		print_r($tables);
		$retArr = array("forms" =>$forms, "tables" => $tables);
		return $retArr;
	}

#$myfile = array(json_decode((fopen("C:\\xampp\\htdocs\\data.json","r")))); 
$json_a = array(json_decode(file_get_contents("C:\\xampp\\htdocs\\data.json"),true));


$a = textractToTable($json_a);
$result = offerTableSceletonMatcher($a['tables']);

// offerTableSceletonMatcher($a['tables'],$a['tables']);



function offerTableSceletonMatcher($tables = array()) {
	$array = array(
		"No"  			=> array("SIRA NO", "Sıra No", "Sıra", "Sira No", "S.No", "No", "NO", "#", "Sıra No.", "Order", "Order No.", "Sira No"),
		"materialDesc"	=> array(
			"Ürün Açıklaması", "Cinsi", "Mal", "Mal/Hizmet", "Açiklama", "Malzeme Tanımı",
			"AÇIKLAMA", "Ürün", "Malzeme", "Malzeme Cinsi", "Ürün Adi", "Material", "Ürün Adı / Ürün Açıklaması", "Malzemenin Cinsi",
			"MALZEMENİN CINSI", "MALZEMELER", "Cinsi", "MALZEME"),
		"supQuantity"	=> array("Miktar", "MİKTAR", "Miktarı", "MİKTARI", "MIKTAR", "ADET", "Adet","MİKTAR/Br.", "MIKTAR/Br."),
		"unite"			=> array("Br.", "Birim", "BİRİM", "BR.","","BIRIM"),
		"unitePrice"	=> array("Birim Fiyat", "BİRİM FİYAT", "B.Fiyat", "Br.Fiyat", "Liste", "Liste Fiyatı", 
			"Liste Fiyat", "BIRIM FİYAT", "BIRIM FIYAT", "NET BIRIM FIYAT", "Net Birim Fiyat", 
			"İskontosuz Birim Fiyat", "ISKONTOSUZ BIRIM FİYAT", "ISKONTOSUZ BR.FYT.", "ISKONTOSUZ BR. FIYAT", "iSKONTOSUZ BR.FYT.",
		"B.Fiyat","Fiyat","FIYAT","Net Fiy."),
		"funitePrice"   => array("İSKONTOLU BİRİM FİYAT", "NİHAi BİRİM FİYAT", "iSKONTOLU BR.FYT."),
		"discountRatio" => array("ISKONTO ORANI","İsk.", "İskonto", "İSKONTO", "ARTIRIM", "İNDİRİM", "İndirim Oranı", "İskonto Oranı", "İsk. (%)","Isk."),
		"supBrands"		=> array("Marka", "Marka/Model", "Brand", "MARKA", "MRK", "Model"," Teklif Edilen Markalar"),
		"deliveryDateSup"=> array("Teslim Tarihi"," Temin Tarihi", "Tarih", "Termin Tarihi"),
		"vatRatio"      => array("KDV", "K.D.V", "kdv", "KDV(%)", "KDV Oranı"),
		"curCode"       => array("PARA BİRİMİ", "PARA BIRIMI", "PARA BR."),
	);
	$offerBodyAtlEastCols = array("unitePrice", "funitePrice", "discountRatio");// teklif body içinde en azından satırlarda bunlardan biri yada bir kaçı olsun ki işe yarasın
	$virtualCols = array("currencyID" => "curCode", "curID"=> "curCode");//Çevrim Değerleri
	$arraySpecs  = array(
		"supQuantity"   	=> array("simpleUnwanted", "turkishDecimal") , 
		"discountRatio" 	=> array("simpleUnwanted", "turkishDecimal") , 
		"unitePrice" 		=> array("simpleUnwanted", "turkishDecimal") ,
		"funitePrice" 		=> array("simpleUnwanted", "turkishDecimal") ,
		"deliveryDateSup" 	=> array("simpleUnwanted", "turkishDate") ,
		"currencyID" 		=> array("simpleUnwanted", "convertCurID"),
		"curID" 		    => array("simpleUnwanted", "convertCurID"),
		"materialDesc" 		=> array("simpleUnwanted"),
		"brandName" 		=> array("simpleUnwanted"),
		"supBrands" 		=> array("simpleUnwanted"),
		"No" 		        => array("simpleUnwanted"),
		"unite" 		    => array("simpleUnwanted"),
		"vatRatio" 		    => array("simpleUnwanted", "turkishDecimal"),
	);
	$retArr      = array();
	$reHeader    = array(); 
	$headercont  = array();
	$sameVals    = array();
	$offerReData = array();
	
	foreach($tables as $t) 
	{
		
		$header = $t['header'];
		foreach($header as $h)
		{
			
			foreach($array as $k => $v)
			{
				if(!isset($reHeader[$k]))
				{
					$tempVal = specialSoundex($h, $v, false, 60);
					$srcVal  = null;
					if(!empty($tempVal))
					{
						$srcVal = $tempVal['val'];
						$possib = $tempVal['possibility'];
						$isExact= $tempVal['isExactRs'];
					}
					if(!empty($srcVal))
					{
						
						$reHeader[$k]   = $h;	
						$headercont[$k] = array("possibility" => $possib ); 		
						break;
					}
				}else
				{
					if($headercont[$k]['possibility'] < 100)
					{
						$tempVal = specialSoundex($h, $v, false, 60);
						$srcVal  = null;
						if(!empty($tempVal))
						{
							$srcVal = $tempVal['val'];
							$possib = $tempVal['possibility'];
							$isExact= $tempVal['isExactRs'];
						}
						if(!empty($srcVal) && $headercont[$k]['possibility'] < $possib)
						{
							$reHeader[$k]   = $h;	
							$headercont[$k] = array("possibility" => $possib ); 		
							break;
						}
					}
				}	
			}	
		}
		$body 	 = $t['body'];
		$j   	 = 0;
		$numOfhd = count($reHeader);
		$items   = array();
		foreach($body as $b)
		{
			$items[] = count($b);
		}	
		$array_depth = max($items);
		
		if($numOfhd > 2 )
		{
			for($j = 0 ; $j < $array_depth; $j++)
			{				
				foreach($reHeader as $krh => $vrh)
				{	
					
					if(isset($body[$vrh][$j] ))
					{
						$filtArr = isset($arraySpecs[$krh]) ? $arraySpecs[$krh] : array();
						//print($body[$vrh][$j]);
						$temVal  = filterAIValueByCustomRules($body[$vrh][$j], $filtArr);
						$retArr[$j][$krh] = $temVal;
						
					}
				}
				
				/***ÖZEL DURUM ---PARA BİRİMİ ANLAMA */
				foreach($reHeader as $krh => $vrh)
				{
					
					if(isset($body['EXPENSE_ROW'][$j]) && !isset($retArr[$j]["curCode"]))
					{
						$tempVal = detectCurrencyFromInnerText($body['EXPENSE_ROW'][$j] , "CODE");
						if(!empty($tempVal))
						{
							$retArr[$j]["curCode"] = $tempVal;
						}
					}
				}

				foreach($virtualCols as $kv => $vb)// Ek çevrim değerleri, para birimi gibi
				{
					if(isset($retArr[$j][$vb]))
					{
						$filtArr = isset($arraySpecs[$kv]) ? $arraySpecs[$kv] : array();
						$temVal  = filterAIValueByCustomRules($retArr[$j][$vb], $filtArr);
						$retArr[$j][$kv] = $temVal;
					}
				}
			}
			//break;//birden fazla tablo olduğunda göbdek için bu yeterli
		}	
	}

	if(count($retArr) > 0)
	{
		$i = 0;			
		foreach($retArr as $k => $r) 
		{
			if($i == 0)
			{
				$sameVals = $r;
			}
			foreach($r as $kk => $vv)
			{
				if(isset($sameVals[$kk]) && $sameVals[$kk] != $vv)
				{
					unset($sameVals[$kk]);
				}
			}
			$i++;
		}
	}

	
	return array("tables" => $retArr, "sameVals" => $sameVals, "fixTable" => $offerReData ) ;
}
function specialSoundex($val, $words = array(), $metaphone = false, $minPossibility = 70, $showresult = false) {		
	if(!empty($val) && !empty($words))
	{
		$retVal	     = "";
		$isExactRs	 = false;
		$possibility = 0;
		/** 1 levenstein */
		$sensitivity = 3;//max
		$shortest    = -1;
		$method      = 0;
		foreach ($words as $word) 
		{
			$lev = levenshtein($val, $word);
			if ($lev == 0) 
			{
				$closest     = $word;
				$shortest    = 0;
				$possibility = 100;
				$isExactRs   = true;
				$method      = 1;
				break;
			}
			if ($lev <= $shortest || $shortest < 0) 
			{
				$closest  = $word;
				$shortest = $lev;
			}
		}
		if($shortest <= $sensitivity)
		{
			$retVal 	= $closest;
			$isExactRs  = false;
			$possibility= 100 - ($shortest * 10);
			$method     = 1;
			//echo $possibility;echo "-1--".$val."->".$closest."<br>";
		} 

		/* 3 similar text*/
		if(!$isExactRs || $possibility < 100)
		{
			foreach ($words as $word) 
			{
				$temp = similar_text($val, $word); 
				$max  = max(strlen($val), strlen($word));
				$newp = $temp / $max * 100;
				///echo $newp;echo "--2--".$val."->".$word."<br>";
				if($newp > $possibility)
				{
					$possibility = $newp;
					$retVal 	 = $word;
					$isExactRs   = false;
					$method      = 3;
				}
			}
		}

		/** 2 metaphone */
		if((!$isExactRs || $possibility < 100) && $metaphone)
		{
			$p1   = metaphone($val);
			$diff = 0;
			foreach ($words as $word) 
			{
				$p2   = metaphone($word);
				if($p1 == $p2)
				{
					$retVal 	 = $word;
					$isExactRs   = false;
					$newp        = 80;
					$method      = 2;
				}else
				{
					$diff = abs(strlen($p1)-strlen($p2));
					$newp = 100 - ($diff * 10);
				}				
				if($newp > $possibility && $newp > 90)
				{
					$possibility = $newp;
					$retVal 	 = $word;
					$isExactRs   = false;
					$method      = 2;
				}
			}
		}

		/** 4 preg match */
		if((!$isExactRs || $possibility < 100))
		{
			$wordArr = explode(" ", trim($word));
			$valArr  = explode(" ", trim($val));
			$numOfPreg= 0 ;
			if(count($wordArr) > 1 && count($valArr) > 1 )
			{
				foreach($wordArr as $wor)
				{
					foreach($valArr as $var)
					{							
						if(!empty($var) && !empty($wor))
						{
							// if (like_match("%".$var."%", $wor)) 
							// {
							// 	$numOfPreg++;
							// } 
						}									
					}
				}
				$newp = ($numOfPreg / count($wordArr) * 100 )- 25;
				if($newp > $possibility && $newp > 60)
				{
					$possibility = $newp;
					$retVal 	 = $word;
					$isExactRs   = false;
					$method      = 4;
				}
			}
		}
		if($showresult){

			// getpre(
			// 	array(
			// 		"isExactRs" 	=> $isExactRs, 
			// 		"possibility" 	=> $possibility, 
			// 		"val" 			=> $retVal, 
			// 		"method" 		=> $method, 
			// 		"srcval" 		=> $val)
			// );
		}
		if($isExactRs || $possibility >= $minPossibility )
		{
			
			return array("isExactRs" => $isExactRs, "possibility" => $possibility, "val" => $retVal, "method" => $method, "srcval" => $val );
		}else
		{
			return "";
		}
	}else
	{
		return "";
	}
	

}
function filterAIValueByCustomRules($val, $rules) {
		
	$reval = $val;
	if(!empty($val))
	{
		if(count($rules) > 0)
		{
			foreach($rules as $r )
			{
				$val = $reval;
				switch($r)
				{
					case "simpleUnwanted":
						$val2  = str_replace(array(":", "*", "**", "***", "!", " : "), '', $val);
						$val2  = filter_var($val2); 
						$reval = $val2;
					break;	

					case "turkishChar":
						$val2  = str_replace(array("Í"), array("İ"), $val);
						$val2  = filter_var($val2); 
						$reval = $val2;
					break;
					
					case "convertInteger":
						$val2 =  preg_replace("/[^0-9.,]/", "", $val);
						$reval = (int)$val2 ;
					break;	
					
					case "turkishDecimal":
						$val2     = preg_replace("/[^0-9.,]/", "", $val);
						$pointArr = explode(".", $val2);
						$commaArr = explode(",", $val2);
						$lang     = "TR";
						/*
						if(count($commaArr) == 2)
						{
							$lang = "TR";
						}else if(count($commaArr) > 2)
						{
							$lang = "EN";
						}
						else if(count($pointArr) == 2 && ($val2) >= 1000)
						{
							$lang = "TR";
						}else if(count($pointArr) == 2 )
						{
							$lang = "EN";
						} else
						{
							$lang = "TR";
						} 
						getpre($lang);exit;
						*/
						if($lang == "TR")
						{
							$reval = ($val2);	
						}else
						{
							// $reval = userDoubleView($val2);
						}
					break;	
					
					case "turkishDate":
						// $reval = turkishDate($val);
					break;						
					
					case "convertCurID":
						switch($val)
						{
							case ""		:
							case null	:
							case "TL"	:
							case "TURK LIRASI":
							case "Türk Lirası":
							case "₺"	:
							case "TRY"	:
								$reval  = 1;
							break;								
							
							case "Euro":
							case "EURO":
							case "AVRO":
							case "Avro":
							case "€":
							case "EUR":
								$reval  = 2;
							break;								
							
							case "USD":
							case "Usd":
							case "Dolar":
							case "Amerikan Doları":
							case "$":
							case "USA Dolar":
								$reval  = 3;
							break;							
							
							case "GBP":
							case "gbp":
							case "Sterlin":
							case "İngiliz Sterlini":
							case "£":
								$reval  = 4;
							break;
						}
					break;

					case "convertGender":
						switch($val)
						{
							case "E/ M":
							case "E / M":
							case "E/M":
							case "E":
							case "M":
								$reval  = "ERKEK";
							break;								
							
							case "K/ F":
							case "K / F":
							case "K/F":
							case "K":
							case "F":
								$reval  = "KADIN";
							break;
						}
					break;

					case "convertNationality":
						switch($val)
						{
							case "T.C./TUR":
							case "T.C.":
							case "TUR":
								$reval  = 1;
							break;
						}
					break;
					
					case "ucwords":
						$reval = ucwords(strtolower($val));
					break;

					case "birthPlaceAndDate":
						$arr 	= strpos($val, " / ") === false ? explode("/", $val) : explode(" / ", $val);
						// $reval 	= count($arr) > 1 ? $arr[0] . " / " . turkishDate($arr[1]) : "";
					break;
				}
			}
		}
	}

	return $reval;
}
function detectCurrencyFromInnerText($text, $rType = "INT") {
	$caughtElem = "";
	$retVal     = null;
	if(!empty($text))
	{
		$wordArr = explode(" ", trim($text));
		$arrTL   = array("TL", "TÜRK LİRASI", "₺", "TRY", "Türk Lirası");
		$arrUsd  = array("$", "USD", "DOLAR", "Amerikan Doları", "USA Dolar");
		$arrEuro = array("€", "Avro", "Euro");
		$arrGbp  = array("£", "GBP", "Sterlin", "İngiliz Sterlini");
		foreach($wordArr as $wor)
		{
			if(in_array($wor, $arrTL))
			{
				$caughtElem  = 1;
				break;
			}
			if(in_array($wor, $arrUsd))
			{
				$caughtElem  = 3;
				break;
			}
			if(in_array($wor, $arrEuro))
			{
				$caughtElem  = 2;
				break;
			}
			if(in_array($wor, $arrGbp))
			{
				$caughtElem  = 4;
				break;
			}
		}		
	}
	if(!empty($caughtElem))
	{
		switch($rType)
		{
			case "INT":
				$retVal = $caughtElem;
			break;

			case "CODE":
				switch($caughtElem)
				{
					case 1:
						$retVal = "TL";
					break;						
					
					case 2:
						$retVal = "EURO";
					break;	

					case 3:
						$retVal = "USD";
					break;						
					
					case 4:
						$retVal = "GBP";
					break;
				}
			break;
		}
	}
	return $retVal;
}
// echo($a);